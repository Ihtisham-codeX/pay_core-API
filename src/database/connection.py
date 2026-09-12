"""
Database connection — with automatic recovery.

WHY THIS FILE LOOKS THE WAY IT DOES:
─────────────────────────────────────────────────────────────────────────────
The database is a Neon serverless PostgreSQL (see PG_HOST in .env). Neon
closes connections that sit idle for a few minutes. Our backend keeps ONE
shared connection for the whole app, so in practice this happens:

    1. App starts, connects, everything works.
    2. You grab coffee. Neon drops the idle connection.
    3. Next request → psycopg2 raises InterfaceError("connection already
       closed") → FastAPI returns 500 for every DB-touching route.

SYMPTOM WE SAW: /auth/login returning 422 for bad input (validation runs
BEFORE the DB, so it still worked) but 500 for perfectly valid requests.

THE FIX: `conn` below is a small proxy that behaves exactly like the real
psycopg2 connection (every repository keeps doing `conn.cursor()`), but
checks liveness before handing out a cursor and transparently reconnects
when the socket has died. During active use the check is skipped, so there
is no extra round-trip on hot paths.
"""

import threading
import time

import psycopg2

from src.config import settings

# After this many seconds of silence we re-verify the socket before use.
# Neon's idle cutoff is ~5 minutes, so 60s gives a wide safety margin.
_IDLE_RECHECK_SECONDS = 60


class _ReconnectingConnection:
    """Stand-in for a psycopg2 connection that heals itself after drops."""

    def __init__(self):
        self._conn = None
        self._last_used = 0.0
        self._lock = threading.Lock()  # reconnect storms: one at a time

    def _connect(self) -> None:
        self._conn = psycopg2.connect(
            host=settings.PG_HOST,
            port=settings.PG_PORT,
            dbname=settings.PG_DATABASE,
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            sslmode=settings.PG_SSLMODE,
            connect_timeout=15,
        )
        self._last_used = time.monotonic()
        print("Database connected successfully.")

    def _ensure_alive(self) -> None:
        # Fast path: used recently and psycopg2 thinks it's open → trust it.
        recently_used = (time.monotonic() - self._last_used) < _IDLE_RECHECK_SECONDS
        if self._conn is not None and not self._conn.closed and recently_used:
            return

        # Slow path: idle for a while (or unknown state) → cheap ping first.
        if self._conn is not None and not self._conn.closed:
            try:
                cur = self._conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                self._conn.rollback()  # leave the connection idle-clean
                return                 # socket still alive, nothing to do
            except psycopg2.OperationalError:
                pass  # dead socket — fall through and reconnect

        try:
            if self._conn is not None:
                self._conn.close()
        except Exception:
            pass
        self._connect()

    # ── The one method every repository calls ────────────────────────────
    def cursor(self, *args, **kwargs):
        with self._lock:
            self._ensure_alive()
        return self._conn.cursor(*args, **kwargs)

    # ── Everything else (commit, rollback, closed…) delegates as-is ──────
    def __getattr__(self, name):
        return getattr(self._conn, name)


conn = _ReconnectingConnection()

# Fail fast at startup: if the database is truly unreachable, the app should
# refuse to boot (same behavior as the old module-level connect).
try:
    conn._ensure_alive()
except Exception as e:
    print(f"Database connection failed: {e}")
    raise RuntimeError(f"Could not connect to PostgreSQL: {e}")

-- ============================================================
--  PAY_CORE  —  Stage 1 Schema
--  Tables:  users  |  refresh_tokens  |  wallets
-- ============================================================


-- ─── Users ───────────────────────────────────────────────────────────────────
-- Stores all registered users.
-- `status` controls whether the account is active or suspended.
-- Passwords are NEVER stored in plain text — only the bcrypt hash.

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL        PRIMARY KEY,
    email         VARCHAR(255)  NOT NULL UNIQUE,
    username      VARCHAR(100)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    first_name    VARCHAR(100)  NOT NULL,
    last_name     VARCHAR(100)  NOT NULL,
    phone         VARCHAR(20),
    role          VARCHAR(20)   NOT NULL DEFAULT 'user',   -- 'user' | 'admin'
    status        VARCHAR(20)   NOT NULL DEFAULT 'active', -- 'active' | 'suspended'
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- ─── Refresh Tokens ──────────────────────────────────────────────────────────
-- Persists refresh tokens so we can:
--   1. Validate they haven't been rotated/revoked (token rotation strategy)
--   2. Invalidate all sessions for a user on logout / password change
--
-- Workflow:
--   Login  → INSERT token
--   Refresh → DELETE old token → INSERT new token  (one-time use)
--   Logout  → DELETE token

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id         SERIAL        PRIMARY KEY,
    user_id    INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT          NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ   NOT NULL,
    created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- ─── Wallets ─────────────────────────────────────────────────────────────────
-- Every user gets exactly one wallet (1:1 with users).
-- Balance is stored as INTEGER in the smallest currency unit (paisa for PKR)
-- to avoid floating-point arithmetic errors. Example: 100,000 = 1000.00 PKR.
--
-- Stage 2 will add row-level locking (SELECT … FOR UPDATE) during transfers
-- to prevent the double-spend race condition.

CREATE TABLE IF NOT EXISTS wallets (
    id         SERIAL        PRIMARY KEY,
    user_id    INTEGER       NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    balance    BIGINT        NOT NULL DEFAULT 0 CHECK (balance >= 0),
    currency   VARCHAR(10)   NOT NULL DEFAULT 'PKR',
    status     VARCHAR(20)   NOT NULL DEFAULT 'active', -- 'active' | 'frozen'
    created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- ─── Triggers ────────────────────────────────────────────────────────────────
-- Automatically update the `updated_at` column whenever a row is modified.

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER wallets_updated_at
    BEFORE UPDATE ON wallets
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

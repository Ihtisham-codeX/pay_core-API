# Load environment variables before anything else
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from src.core.redis import close_redis_client, get_redis_client

# Routers
from src.api.routers.auth         import router as auth_router
from src.api.routers.users        import router as users_router
from src.api.routers.wallets      import router as wallets_router
from src.api.routers.transfers    import router as transfers_router     # Stage 2
from src.api.routers.transactions import router as transactions_router  # Stage 2

# Middleware
from src.middleware.logging_middleware import LoggingMiddleware
from src.middleware.auth_middleware    import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_redis_client()
    yield
    close_redis_client()


# ─── Application ─────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "PAY_CORE — Payment API",
    description = "A financial-grade payment backend. Stage 1: Users · Auth · Wallets",
    version     = "1.0.0",
    lifespan    = lifespan,
)


# ─── Middleware ───────────────────────────────────────────────────────────────
# Execution order (last registered → runs first):
#   AuthMiddleware  →  LoggingMiddleware  →  route handler
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)


# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(wallets_router)
app.include_router(transfers_router)
app.include_router(transactions_router)

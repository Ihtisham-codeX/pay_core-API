from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from src.security.jwt import verify_access_token


# centralises auth logic , individual routes never decode tokens themselves


PUBLIC_ROUTES = {
    "/auth/register",
    "/auth/login",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # Allow public routes through without any token check
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        # Read token from HttpOnly cookie
        token = request.cookies.get("access_token")

        if token is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required. Please log in."}
            )

        # Verify signature and decode
        payload = verify_access_token(token)

        if payload is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired access token."}
            )

        # Inject user data into request state for downstream use
        request.state.user = payload

        return await call_next(request)

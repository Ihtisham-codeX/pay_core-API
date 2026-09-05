import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.time()

        response = await call_next(request)

        duration = round(time.time() - start_time, 4)

        print(
            f"{request.method:<7} {request.url.path:<40} "
            f"| {response.status_code} "
            f"| {duration}s "
            f"| {request.client.host}"
        )

        return response

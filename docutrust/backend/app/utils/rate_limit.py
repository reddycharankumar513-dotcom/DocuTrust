import time
from collections import defaultdict, deque

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import settings


class InMemoryRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        now = time.monotonic()
        window_start = now - settings.rate_limit_window_seconds
        client = request.client.host if request.client else "unknown"
        bucket = self.requests[client]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= settings.rate_limit_requests:
            return Response("Rate limit exceeded", status_code=429)

        bucket.append(now)
        return await call_next(request)

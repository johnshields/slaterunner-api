import time
from typing import Dict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()


def _get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check proxy forwarded IP header
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Use direct client IP as fallback
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""

    def __init__(self, app, requests_per_minute: int = None, window_size: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.window_size = window_size or settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        # Exclude health check endpoints from rate limiting
        if request.url.path in ["/health", "/health/simple"]:
            return await call_next(request)

        client_ip = _get_client_ip(request)
        current_time = time.time()

        # Remove expired request timestamps
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_size
            ]
        else:
            self.requests[client_ip] = []

        # Verify client has not exceeded rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded for IP: %s", client_ip)
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded",
                    "details": {
                        "limit": self.requests_per_minute,
                        "window_seconds": self.window_size,
                        "retry_after": self.window_size
                    }
                }
            )

        # Track current request timestamp
        self.requests[client_ip].append(current_time)

        # Process request and add rate limit headers
        response = await call_next(request)
        remaining = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Apply security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Enable HSTS for production environment
        if settings.is_production():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring and debugging"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log incoming request
        logger.info("Request: %s %s from %s", request.method, request.url.path, request.client.host if request.client else "unknown")

        # Process request and calculate timing
        response = await call_next(request)

        # Log response details
        process_time = time.time() - start_time
        logger.info("Response: %s in %.3fs", response.status_code, process_time)

        # Include processing time in response headers
        response.headers["X-Process-Time"] = str(process_time)

        return response

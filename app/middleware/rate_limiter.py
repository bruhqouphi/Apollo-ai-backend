"""
Rate Limiting Middleware
Implements request rate limiting to prevent abuse.
"""

import time
import logging
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation using sliding window."""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """Check if request is allowed and return remaining requests."""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > window_start
            ]
        else:
            self.requests[client_ip] = []
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False, 0
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        return True, remaining

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware function."""
    client_ip = request.client.host
    
    # Skip rate limiting for health checks
    if request.url.path == "/" or request.url.path == "/health":
        return await call_next(request)
    
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": 60
            },
            headers={"Retry-After": "60"}
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response 
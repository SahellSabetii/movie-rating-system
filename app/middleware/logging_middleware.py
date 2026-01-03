import time
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger("movie_rating")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        request_id = request.headers.get("X-Request-ID", "N/A")
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "route": request.url.path
            }
        )
        
        try:
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "route": request.url.path
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                    "route": request.url.path
                },
                exc_info=True
            )
            raise


def setup_request_id():
    """Create a request ID for tracking"""
    import uuid
    return str(uuid.uuid4())

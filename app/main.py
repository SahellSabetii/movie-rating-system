import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers import movies_router, directors_router, genres_router, ratings_router
from app.exceptions import (
    MovieRatingError, 
    NotFoundError, 
    ValidationError, 
    AlreadyExistsError,
    DatabaseError
)
from app.schemas.response import create_error_response
from app.logging_config import setup_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware


logger = get_logger()
setup_logging()


app = FastAPI(
    title="Movie Rating System API",
    description="A RESTful API for managing movies, directors, genres, and ratings",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    logger.warning(
        f"Resource not found: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": "NotFoundError",
            "error_message": str(exc)
        }
    )
    return JSONResponse(
        status_code=404,
        content=create_error_response(404, str(exc))
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": "ValidationError",
            "error_message": str(exc)
        }
    )
    return JSONResponse(
        status_code=422,
        content=create_error_response(422, str(exc))
    )

@app.exception_handler(AlreadyExistsError)
async def already_exists_exception_handler(request: Request, exc: AlreadyExistsError):
    logger.warning(
        f"Resource already exists: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": "AlreadyExistsError",
            "error_message": str(exc)
        }
    )
    return JSONResponse(
        status_code=409,
        content=create_error_response(409, str(exc))
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": "DatabaseError",
            "error_message": str(exc)
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, str(exc))
    )

@app.exception_handler(MovieRatingError)
async def movie_rating_exception_handler(request: Request, exc: MovieRatingError):
    logger.error(
        f"Movie rating error: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": "MovieRatingError",
            "error_message": str(exc)
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, str(exc))
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "route": request.url.path,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, f"Internal server error: {str(exc)}")
    )

app.include_router(movies_router)
app.include_router(directors_router)
app.include_router(genres_router)
app.include_router(ratings_router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Movie Rating System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "movies": "/api/v1/movies",
            "directors": "/api/v1/directors", 
            "genres": "/api/v1/genres",
            "ratings": "/api/v1/ratings"
        }
    }

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": "movie-rating-system"}

@app.get("/api/version")
async def api_version():
    logger.debug("API version endpoint accessed")
    return {
        "api": "Movie Rating System",
        "version": "1.0.0",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Movie Rating System API")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

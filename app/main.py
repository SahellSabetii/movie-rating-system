from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers import movies_router, directors_router, genres_router, ratings_router
from app.exceptions import MovieRatingError, NotFoundError, ValidationError, AlreadyExistsError
from app.schemas.response import create_error_response


app = FastAPI(
    title="Movie Rating System API",
    description="A RESTful API for managing movies, directors, genres, and ratings",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content=create_error_response(404, str(exc))
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content=create_error_response(422, str(exc))
    )

@app.exception_handler(AlreadyExistsError)
async def already_exists_exception_handler(request, exc: AlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content=create_error_response(409, str(exc))
    )

@app.exception_handler(MovieRatingError)
async def movie_rating_exception_handler(request, exc: MovieRatingError):
    return JSONResponse(
        status_code=500,
        content=create_error_response(500, str(exc))
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
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
    return {"status": "healthy", "service": "movie-rating-system"}

@app.get("/api/version")
async def api_version():
    return {
        "api": "Movie Rating System",
        "version": "1.0.0",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

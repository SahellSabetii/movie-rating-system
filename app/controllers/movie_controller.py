from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.schemas import (
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    MovieDetailResponse,
    create_success_response,
    create_error_response,
    create_paginated_response
)
from app.services.deps import get_movie_service, get_service_factory, get_rating_service
from app.services.movie_service import MovieService
from app.services.factory import ServiceFactory
from app.services.rating_service import RatingService
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@router.get("/", response_model=dict)
async def get_movies(
    title: Optional[str] = Query(None, description="Search by title"),
    release_year: Optional[int] = Query(None, ge=1888, le=2100, description="Filter by release year"),
    genre: Optional[str] = Query(None, description="Filter by genre name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    movie_service: MovieService = Depends(get_movie_service),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get all movies with pagination and filtering - EXACTLY as specified in PDF
    """
    try:
        skip = (page - 1) * page_size
        
        if title or release_year or genre:
            filtered_movies = []
            
            if title:
                movies = movie_service.search_movies(title_query=title, skip=0, limit=1000)
            else:
                movies = movie_service.get_all_movies(skip=0, limit=1000)
            
            for movie in movies:
                if release_year and movie.release_year != release_year:
                    continue

                if genre:
                    genre_matched = False
                    movie_genres = [g.name.lower() for g in movie.genres] if hasattr(movie, 'genres') else []
                    if genre.lower() in movie_genres:
                        genre_matched = True
                    
                    if not genre_matched:
                        continue
                
                filtered_movies.append(movie)
            
            paginated_movies = filtered_movies[skip:skip + page_size]
            
            response_items = []
            for movie in paginated_movies:
                avg_rating = service_factory.ratings.get_average_rating(movie.id)
                rating_count = len(movie.ratings) if hasattr(movie, 'ratings') else 0
                
                movie_response = MovieResponse(
                    id=movie.id,
                    title=movie.title,
                    release_year=movie.release_year,
                    director={
                        "id": movie.director.id,
                        "name": movie.director.name
                    } if movie.director else None,
                    genres=[genre.name for genre in movie.genres] if hasattr(movie, 'genres') else [],
                    average_rating=avg_rating,
                    ratings_count=rating_count
                )
                response_items.append(movie_response.model_dump())
            
            return create_paginated_response(
                items=response_items,
                page=page,
                page_size=page_size,
                total_items=len(filtered_movies)
            )
        
        all_movies = movie_service.get_all_movies(skip=skip, limit=page_size)
        total_count = movie_service.count_movies()
        
        response_items = []
        for movie in all_movies:
            avg_rating = service_factory.ratings.get_average_rating(movie.id)
            rating_count = len(movie.ratings) if hasattr(movie, 'ratings') else 0
            
            movie_response = MovieResponse(
                id=movie.id,
                title=movie.title,
                release_year=movie.release_year,
                director={
                    "id": movie.director.id,
                    "name": movie.director.name
                } if movie.director else None,
                genres=[genre.name for genre in movie.genres] if hasattr(movie, 'genres') else [],
                average_rating=avg_rating,
                ratings_count=rating_count
            )
            response_items.append(movie_response.model_dump())
        
        return create_paginated_response(
            items=response_items,
            page=page,
            page_size=page_size,
            total_items=total_count
        )
        
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/{movie_id}", response_model=dict)
async def get_movie(
    movie_id: int = Path(..., description="Movie ID"),
    movie_service: MovieService = Depends(get_movie_service),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get movie details by ID - EXACTLY as specified in PDF
    """
    try:
        movie = movie_service.get_movie_with_details(movie_id)
        
        if not movie:
            return create_error_response(404, "Movie not found")
        
        avg_rating = service_factory.ratings.get_average_rating(movie_id)
        rating_count = len(movie.ratings) if hasattr(movie, 'ratings') else 0
        
        movie_detail = MovieDetailResponse(
            id=movie.id,
            title=movie.title,
            release_year=movie.release_year,
            director={
                "id": movie.director.id,
                "name": movie.director.name,
                "birth_year": movie.director.birth_year,
                "description": movie.director.description
            } if movie.director else None,
            genres=[genre.name for genre in movie.genres] if hasattr(movie, 'genres') else [],
            cast=movie.cast,
            average_rating=avg_rating,
            ratings_count=rating_count,
            created_at=movie.created_at.isoformat() if movie.created_at else None,
            updated_at=movie.updated_at.isoformat() if movie.updated_at else None
        )
        
        return create_success_response(movie_detail.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.post("/", response_model=dict, status_code=201)
async def create_movie(
    movie_data: MovieCreate,
    movie_service: MovieService = Depends(get_movie_service),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Create a new movie - EXACTLY as specified in PDF
    """
    try:
        movie = movie_service.create_movie(
            title=movie_data.title,
            director_id=movie_data.director_id,
            release_year=movie_data.release_year,
            cast=movie_data.cast,
            genre_ids=movie_data.genres
        )
        
        created_movie = movie_service.get_movie_with_details(movie.id)
        
        movie_detail = MovieDetailResponse(
            id=created_movie.id,
            title=created_movie.title,
            release_year=created_movie.release_year,
            director={
                "id": created_movie.director.id,
                "name": created_movie.director.name
            } if created_movie.director else None,
            genres=[genre.name for genre in created_movie.genres] if hasattr(created_movie, 'genres') else [],
            cast=created_movie.cast,
            average_rating=None,
            ratings_count=0,
            created_at=created_movie.created_at.isoformat() if created_movie.created_at else None,
            updated_at=created_movie.updated_at.isoformat() if created_movie.updated_at else None
        )
        
        return create_success_response(movie_detail.model_dump())
        
    except ValidationError as e:
        return create_error_response(422, str(e))
    except AlreadyExistsError as e:
        return create_error_response(409, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.put("/{movie_id}", response_model=dict)
async def update_movie(
    movie_id: int = Path(..., description="Movie ID"),
    movie_data: MovieUpdate = Body(...),
    movie_service: MovieService = Depends(get_movie_service),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Update movie information - EXACTLY as specified in PDF
    """
    try:
        update_dict = {}
        if movie_data.title is not None:
            update_dict["title"] = movie_data.title
        if movie_data.director_id is not None:
            update_dict["director_id"] = movie_data.director_id
        if movie_data.release_year is not None:
            update_dict["release_year"] = movie_data.release_year
        if movie_data.cast is not None:
            update_dict["cast"] = movie_data.cast
        
        movie = None
        if update_dict:
            movie = movie_service.update_movie(movie_id=movie_id, **update_dict)
        
        if movie_data.genres is not None:
            movie = movie_service.update_movie_genres(movie_id, movie_data.genres)
        elif not update_dict:
            movie = movie_service.get_movie_with_details(movie_id)
        
        if not movie:
            return create_error_response(404, f"Movie with id {movie_id} not found")
        
        updated_movie = movie_service.get_movie_with_details(movie.id)
        
        avg_rating = service_factory.ratings.get_average_rating(movie_id)
        rating_count = len(updated_movie.ratings) if hasattr(updated_movie, 'ratings') else 0
        
        movie_detail = MovieDetailResponse(
            id=updated_movie.id,
            title=updated_movie.title,
            release_year=updated_movie.release_year,
            director={
                "id": updated_movie.director.id,
                "name": updated_movie.director.name
            } if updated_movie.director else None,
            genres=[genre.name for genre in updated_movie.genres] if hasattr(updated_movie, 'genres') else [],
            cast=updated_movie.cast,
            average_rating=avg_rating,
            ratings_count=rating_count,
            created_at=updated_movie.created_at.isoformat() if updated_movie.created_at else None,
            updated_at=updated_movie.updated_at.isoformat() if updated_movie.updated_at else None
        )
        
        return create_success_response(movie_detail.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except ValidationError as e:
        return create_error_response(422, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int = Path(..., description="Movie ID"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Delete a movie - EXACTLY as specified in PDF
    """
    try:
        result = movie_service.delete_movie(movie_id)
        if not result:
            return create_error_response(404, "Movie not found")
        
        return Response(status_code=204)
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.post("/{movie_id}/ratings", response_model=dict, status_code=201)
async def create_movie_rating(
    movie_id: int = Path(..., description="Movie ID"),
    rating_data: dict = Body(..., example={"score": 8}),
    rating_service: RatingService = Depends(get_rating_service),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Add a rating to a movie - EXACTLY as specified in PDF
    """
    try:
        movie_service = service_factory.movies
        if not movie_service.movie_exists(movie_id):
            return create_error_response(404, "Movie not found")
        
        if "score" not in rating_data:
            return create_error_response(422, "Score is required")
        
        score = rating_data["score"]
        
        if not isinstance(score, int) or not (1 <= score <= 10):
            return create_error_response(422, "Score must be an integer between 1 and 10")
        
        rating = rating_service.create_rating(movie_id=movie_id, score=score)
        
        response = {
            "rating_id": rating.id,
            "movie_id": rating.movie_id,
            "score": rating.score,
            "created_at": rating.created_at.isoformat() if rating.created_at else None
        }
        
        return create_success_response(response)
        
    except ValidationError as e:
        return create_error_response(422, str(e))
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")

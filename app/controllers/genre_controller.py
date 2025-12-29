from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.schemas import (
    GenreCreate,
    GenreUpdate,
    GenreResponse,
    GenreListResponse,
    create_success_response,
    create_error_response,
    create_paginated_response
)
from app.services.deps import get_genre_service
from app.services.genre_service import GenreService
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError

router = APIRouter(prefix="/api/v1/genres", tags=["genres"])


@router.get("/", response_model=dict)
async def get_genres(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by genre name"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get all genres with pagination
    """
    try:
        skip = (page - 1) * page_size
        
        if name:
            genre = genre_service.get_genre_by_name(name)
            genres = [genre] if genre else []
        else:
            genres = genre_service.get_all_genres(skip=skip, limit=page_size)
        
        total_count = genre_service.count_genres()
        
        response_items = []
        for genre in genres:
            genre_response = GenreResponse(
                id=genre.id,
                name=genre.name,
                description=genre.description,
                created_at=genre.created_at.isoformat() if genre.created_at else None
            )
            response_items.append(genre_response.model_dump())
        
        return create_paginated_response(
            items=response_items,
            page=page,
            page_size=page_size,
            total_items=total_count
        )
        
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/{genre_id}", response_model=dict)
async def get_genre(
    genre_id: int = Path(..., description="Genre ID"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get genre details by ID
    """
    try:
        genre = genre_service.get_genre_with_movies(genre_id)
        
        if not genre:
            return create_error_response(404, f"Genre with id {genre_id} not found")
        
        genre_response = GenreResponse(
            id=genre.id,
            name=genre.name,
            description=genre.description,
            created_at=genre.created_at.isoformat() if genre.created_at else None
        )
        
        return create_success_response(genre_response.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.post("/", response_model=dict, status_code=201)
async def create_genre(
    genre_data: GenreCreate,
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Create a new genre
    """
    try:
        genre = genre_service.create_genre(
            name=genre_data.name,
            description=genre_data.description
        )
        
        genre_response = GenreResponse(
            id=genre.id,
            name=genre.name,
            description=genre.description,
            created_at=genre.created_at.isoformat() if genre.created_at else None
        )
        
        return create_success_response(genre_response.model_dump())
        
    except ValidationError as e:
        return create_error_response(422, str(e))
    except AlreadyExistsError as e:
        return create_error_response(409, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.put("/{genre_id}", response_model=dict)
async def update_genre(
    genre_data: GenreUpdate,
    genre_id: int = Path(..., description="Genre ID"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Update genre information
    """
    try:
        genre = genre_service.update_genre(
            genre_id=genre_id,
            name=genre_data.name,
            description=genre_data.description
        )
        
        genre_response = GenreResponse(
            id=genre.id,
            name=genre.name,
            description=genre.description,
            created_at=genre.created_at.isoformat() if genre.created_at else None
        )
        
        return create_success_response(genre_response.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except ValidationError as e:
        return create_error_response(422, str(e))
    except AlreadyExistsError as e:
        return create_error_response(409, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.delete(
    "/{genre_id}",
    responses={
        204: {"description": "Genre deleted successfully"},
        404: {
            "description": "Genre not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "error": {"code": 404, "message": "Genre not found"}
                    }
                }
            }
        }
    }
)
async def delete_genre(
    genre_id: int = Path(..., description="Genre ID"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Delete a genre
    """
    try:
        result = genre_service.delete_genre(genre_id)
        if not result:
            return create_error_response(404, f"Genre with id {genre_id} not found")
        
        return Response(status_code=204)
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")

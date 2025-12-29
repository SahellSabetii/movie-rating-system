from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.schemas import (
    DirectorCreate,
    DirectorUpdate,
    DirectorResponse,
    DirectorListResponse,
    create_success_response,
    create_error_response,
    create_paginated_response
)
from app.services.deps import get_director_service
from app.services.director_service import DirectorService
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError

router = APIRouter(prefix="/api/v1/directors", tags=["directors"])


@router.get("/", response_model=dict)
async def get_directors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by director name"),
    director_service: DirectorService = Depends(get_director_service)
):
    """
    Get all directors with pagination
    """
    try:
        skip = (page - 1) * page_size
        
        if name:
            directors = director_service.search_directors(name, skip=skip, limit=page_size)
        else:
            directors = director_service.get_all_directors(skip=skip, limit=page_size)
        
        total_count = director_service.count_directors()
        
        response_items = []
        for director in directors:
            director_response = DirectorResponse(
                id=director.id,
                name=director.name,
                birth_year=director.birth_year,
                description=director.description,
                created_at=director.created_at.isoformat() if director.created_at else None,
                updated_at=director.updated_at.isoformat() if director.updated_at else None
            )
            response_items.append(director_response.model_dump())
        
        return create_paginated_response(
            items=response_items,
            page=page,
            page_size=page_size,
            total_items=total_count
        )
        
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/{director_id}", response_model=dict)
async def get_director(
    director_id: int = Path(..., description="Director ID"),
    director_service: DirectorService = Depends(get_director_service),
):
    """
    Get director details by ID
    """
    try:
        director = director_service.get_director_with_movies(director_id)
        
        if not director:
            return create_error_response(404, f"Director with id {director_id} not found")
        
        director_response = DirectorResponse(
            id=director.id,
            name=director.name,
            birth_year=director.birth_year,
            description=director.description,
            created_at=director.created_at.isoformat() if director.created_at else None,
            updated_at=director.updated_at.isoformat() if director.updated_at else None
        )
        
        return create_success_response(director_response.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.post("/", response_model=dict, status_code=201)
async def create_director(
    director_data: DirectorCreate,
    director_service: DirectorService = Depends(get_director_service)
):
    """
    Create a new director
    """
    try:
        director = director_service.create_director(
            name=director_data.name,
            birth_year=director_data.birth_year,
            description=director_data.description
        )
        
        director_response = DirectorResponse(
            id=director.id,
            name=director.name,
            birth_year=director.birth_year,
            description=director.description,
            created_at=director.created_at.isoformat() if director.created_at else None,
            updated_at=director.updated_at.isoformat() if director.updated_at else None
        )
        
        return create_success_response(director_response.model_dump())
        
    except ValidationError as e:
        return create_error_response(422, str(e))
    except AlreadyExistsError as e:
        return create_error_response(409, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.put("/{director_id}", response_model=dict)
async def update_director(
    director_data: DirectorUpdate,
    director_id: int = Path(..., description="Director ID"),
    director_service: DirectorService = Depends(get_director_service)
):
    """
    Update director information
    """
    try:
        director = director_service.update_director(
            director_id=director_id,
            name=director_data.name,
            birth_year=director_data.birth_year,
            description=director_data.description
        )
        
        director_response = DirectorResponse(
            id=director.id,
            name=director.name,
            birth_year=director.birth_year,
            description=director.description,
            created_at=director.created_at.isoformat() if director.created_at else None,
            updated_at=director.updated_at.isoformat() if director.updated_at else None
        )
        
        return create_success_response(director_response.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except ValidationError as e:
        return create_error_response(422, str(e))
    except AlreadyExistsError as e:
        return create_error_response(409, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.delete(
    "/{director_id}",
    responses={
        204: {"description": "Director deleted successfully"},
        404: {
            "description": "Director not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "failure",
                        "error": {"code": 404, "message": "Director not found"}
                    }
                }
            }
        }
    }
)
async def delete_director(
    director_id: int = Path(..., description="Director ID"),
    director_service: DirectorService = Depends(get_director_service)
):
    """
    Delete a director
    """
    try:
        result = director_service.delete_director(director_id)
        if not result:
            return create_error_response(404, f"Director with id {director_id} not found")
        
        return Response(status_code=204)
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.schemas import (
    RatingCreate,
    RatingResponse,
    RatingStatsResponse,
    RatingDistributionResponse,
    create_success_response,
    create_error_response,
    create_paginated_response
)
from app.services.deps import get_rating_service, get_service_factory
from app.services.rating_service import RatingService
from app.services.factory import ServiceFactory
from app.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/ratings", tags=["ratings"])


@router.get("/movie/{movie_id}", response_model=dict)
async def get_movie_ratings(
    movie_id: int = Path(..., description="Movie ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Get all ratings for a specific movie
    """
    try:
        skip = (page - 1) * page_size
        
        ratings = rating_service.get_movie_ratings(
            movie_id=movie_id,
            skip=skip,
            limit=page_size
        )
        
        stats = rating_service.get_movie_rating_stats(movie_id)
        total_count = stats.get('count', 0)
        
        response_items = []
        for rating in ratings:
            rating_response = RatingResponse(
                rating_id=rating.id,
                movie_id=rating.movie_id,
                score=rating.score,
                created_at=rating.created_at.isoformat() if rating.created_at else None
            )
            response_items.append(rating_response.model_dump())
        
        return create_paginated_response(
            items=response_items,
            page=page,
            page_size=page_size,
            total_items=total_count
        )
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/movie/{movie_id}/stats", response_model=dict)
async def get_movie_rating_stats(
    movie_id: int = Path(..., description="Movie ID"),
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Get rating statistics for a movie
    """
    try:
        stats = rating_service.get_movie_rating_stats(movie_id)
        
        rating_stats = RatingStatsResponse(
            movie_id=movie_id,
            count=stats.get('count', 0),
            average=stats.get('average'),
            min=stats.get('min'),
            max=stats.get('max')
        )
        
        return create_success_response(rating_stats.model_dump())
        
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/recent", response_model=dict)
async def get_recent_ratings(
    limit: int = Query(50, ge=1, le=100, description="Number of recent ratings"),
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Get most recent ratings
    """
    try:
        ratings = rating_service.get_recent_ratings(limit=limit)
        
        response_items = []
        for rating in ratings:
            rating_response = RatingResponse(
                rating_id=rating.id,
                movie_id=rating.movie_id,
                score=rating.score,
                created_at=rating.created_at.isoformat() if rating.created_at else None
            )
            response_items.append(rating_response.model_dump())
        
        return create_success_response(response_items)
        
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.get("/overall-stats", response_model=dict)
async def get_overall_rating_stats(
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Get overall rating statistics
    """
    try:
        stats = rating_service.calculate_overall_stats()
        
        return create_success_response(stats)
        
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")


@router.post("/", response_model=dict, status_code=201)
async def create_rating(
    rating_data: RatingCreate,
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Create a new rating
    """
    try:
        rating = rating_service.create_rating(
            movie_id=rating_data.movie_id,
            score=rating_data.score
        )
        
        rating_response = RatingResponse(
            rating_id=rating.id,
            movie_id=rating.movie_id,
            score=rating.score,
            created_at=rating.created_at.isoformat() if rating.created_at else None
        )
        
        return create_success_response(rating_response.model_dump())
        
    except ValidationError as e:
        return create_error_response(422, str(e))
    except NotFoundError as e:
        return create_error_response(404, str(e))
    except Exception as e:
        return create_error_response(500, f"Internal server error: {str(e)}")

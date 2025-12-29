from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RatingCreate(BaseModel):
    """Schema for creating a rating"""
    movie_id: int = Field(..., ge=1)
    score: int = Field(..., ge=1, le=10)
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError('Score must be between 1 and 10')
        return v


class RatingResponse(BaseModel):
    """Schema for rating response"""
    rating_id: int
    movie_id: int
    score: int
    created_at: Optional[str] = None


class RatingStatsResponse(BaseModel):
    """Schema for rating statistics"""
    movie_id: int
    count: int = 0
    average: Optional[float] = Field(None, ge=0, le=10)
    min: Optional[int] = Field(None, ge=1, le=10)
    max: Optional[int] = Field(None, ge=1, le=10)


class RatingDistributionResponse(BaseModel):
    """Schema for rating distribution"""
    score: int
    count: int = 0

from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class MovieCreate(BaseModel):
    """Schema for creating a movie"""
    title: str = Field(..., min_length=1, max_length=300)
    director_id: int = Field(..., ge=1)
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    cast: Optional[str] = Field(None, max_length=1000)
    genres: List[int] = Field(default=[], description="List of genre IDs")
    
    @field_validator('genres')
    @classmethod
    def validate_genres(cls, v: List[int]) -> List[int]:
        if not all(isinstance(genre_id, int) and genre_id > 0 for genre_id in v):
            raise ValueError('All genre IDs must be positive integers')
        return v


class MovieUpdate(BaseModel):
    """Schema for updating a movie"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    director_id: Optional[int] = Field(None, ge=1)
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    cast: Optional[str] = Field(None, max_length=1000)
    genres: Optional[List[int]] = Field(None)


class MovieResponse(BaseModel):
    """Schema for movie response in list"""
    id: int
    title: str
    release_year: Optional[int] = None
    director: Optional[dict] = None
    genres: List[str] = Field(default=[])
    average_rating: Optional[float] = Field(None, ge=0, le=10)
    ratings_count: int = 0


class MovieDetailResponse(BaseModel):
    """Schema for detailed movie response"""
    id: int
    title: str
    release_year: Optional[int] = None
    director: Optional[dict] = None
    genres: List[str] = Field(default=[])
    cast: Optional[str] = None
    average_rating: Optional[float] = Field(None, ge=0, le=10)
    ratings_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MovieListResponse(BaseModel):
    """Schema for paginated movie list"""
    page: int
    page_size: int
    total_items: int
    items: list[MovieResponse]

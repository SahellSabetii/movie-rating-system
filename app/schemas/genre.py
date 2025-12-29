from typing import Optional

from pydantic import BaseModel, Field


class GenreCreate(BaseModel):
    """Schema for creating a genre"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GenreUpdate(BaseModel):
    """Schema for updating a genre"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GenreResponse(BaseModel):
    """Schema for genre response"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None


class GenreWithMoviesResponse(GenreResponse):
    """Genre response with movie count"""
    movie_count: Optional[int] = 0


class GenreListResponse(BaseModel):
    """Schema for paginated genre list"""
    page: int
    page_size: int
    total_items: int
    items: list[GenreResponse]

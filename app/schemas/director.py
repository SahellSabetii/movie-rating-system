from typing import Optional

from pydantic import BaseModel, Field


class DirectorCreate(BaseModel):
    """Schema for creating a director"""
    name: str = Field(..., min_length=1, max_length=200)
    birth_year: Optional[int] = Field(None, ge=1800, le=2100)
    description: Optional[str] = Field(None, max_length=1000)


class DirectorUpdate(BaseModel):
    """Schema for updating a director"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    birth_year: Optional[int] = Field(None, ge=1800, le=2100)
    description: Optional[str] = Field(None, max_length=1000)


class DirectorResponse(BaseModel):
    """Schema for director response"""
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DirectorWithMoviesResponse(DirectorResponse):
    """Director response with movie count"""
    movie_count: Optional[int] = 0


class DirectorListResponse(BaseModel):
    """Schema for paginated director list"""
    page: int
    page_size: int
    total_items: int
    items: list[DirectorResponse]

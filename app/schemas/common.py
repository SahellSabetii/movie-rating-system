from typing import Optional

from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    """Pagination query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")


class MovieFilterQuery(PaginationQuery):
    """Movie filter query parameters"""
    title: Optional[str] = Field(None, description="Search by title (partial match)")
    release_year: Optional[int] = Field(None, ge=1888, le=2100, description="Filter by release year")
    genre: Optional[str] = Field(None, description="Filter by genre name")

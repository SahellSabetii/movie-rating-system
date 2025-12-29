from typing import TypeVar, Generic, Optional, Any

from pydantic import BaseModel


T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response schema"""
    status: str = "success"
    data: T


class ErrorDetail(BaseModel):
    """Error detail schema"""
    code: int
    message: str


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    status: str = "failure"
    error: ErrorDetail


class PaginatedData(BaseModel, Generic[T]):
    """Paginated data structure"""
    page: int
    page_size: int
    total_items: int
    items: list[T]


def create_success_response(data: Any) -> dict:
    """Helper to create success response"""
    return SuccessResponse(data=data).model_dump()


def create_error_response(code: int, message: str) -> dict:
    """Helper to create error response"""
    return ErrorResponse(
        error=ErrorDetail(code=code, message=message)
    ).model_dump()


def create_paginated_response(
    items: list,
    page: int,
    page_size: int,
    total_items: int
) -> dict:
    """Helper to create paginated response"""
    return SuccessResponse(
        data=PaginatedData(
            page=page,
            page_size=page_size,
            total_items=total_items,
            items=items
        )
    ).model_dump()

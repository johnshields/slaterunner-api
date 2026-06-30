from typing import Generic, TypeVar, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard API response with pagination metadata."""
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Response message")
    data: list[T] = Field(..., description="List of items for the current page")
    count: int = Field(..., description="Total number of items available")
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Number of items skipped")

    @classmethod
    def create(cls, data: list[T], count: int, limit: int, offset: int, message: str = "Retrieved successfully"):
        """Create a paginated response."""
        return cls(
            status="success",
            message=message,
            data=data,
            count=count,
            limit=limit,
            offset=offset
        )


def create_paginated_response(items: list[Any], count: int, limit: int, offset: int, message: str = "Retrieved successfully") -> dict:
    """Helper to create paginated response dict."""
    return {
        "status": "success",
        "message": message,
        "data": items,
        "count": count,
        "limit": limit,
        "offset": offset
    }


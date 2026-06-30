from typing import Generic, TypeVar, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Response message")
    data: T = Field(..., description="Response data")

    @classmethod
    def create(cls, data: T, message: str = "Operation successful"):
        """Create a standard API response."""
        return cls(
            status="success",
            message=message,
            data=data
        )


def create_response(data: Any, message: str = "Operation successful") -> dict:
    """Helper to create standard response dict."""
    return {
        "status": "success",
        "message": message,
        "data": data
    }


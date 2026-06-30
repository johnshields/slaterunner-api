from fastapi import HTTPException
from typing import Any, Dict, Optional


class SlateRunnerException(Exception):
    """Base exception for Slate Runner application"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SlateRunnerException):
    """Raised when input validation fails"""
    pass


class BusinessLogicError(SlateRunnerException):
    """Raised when business logic constraints are violated"""
    pass


class DatabaseError(SlateRunnerException):
    """Raised when database operations fail"""
    pass


class NotFoundError(SlateRunnerException):
    """Raised when a requested resource is not found"""
    pass


class ConflictError(SlateRunnerException):
    """Raised when a resource conflict occurs"""
    pass


class UnauthorizedError(SlateRunnerException):
    """Raised when authorization fails"""
    pass


def create_http_exception(
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create a standardised HTTP exception"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )


def handle_slate_runner_exception(exc: SlateRunnerException) -> HTTPException:
    """Convert SlateRunnerException to appropriate HTTPException"""

    if isinstance(exc, ValidationError):
        return create_http_exception(400, exc.message, exc.details)
    elif isinstance(exc, BusinessLogicError):
        return create_http_exception(422, exc.message, exc.details)
    elif isinstance(exc, DatabaseError):
        return create_http_exception(500, "Database operation failed", exc.details)
    elif isinstance(exc, NotFoundError):
        return create_http_exception(404, exc.message, exc.details)
    elif isinstance(exc, ConflictError):
        return create_http_exception(409, exc.message, exc.details)
    elif isinstance(exc, UnauthorizedError):
        return create_http_exception(401, exc.message, exc.details)
    else:
        return create_http_exception(500, "Internal server error", {"original_error": exc.message})

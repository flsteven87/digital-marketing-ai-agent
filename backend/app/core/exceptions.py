from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(AppException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class UnprocessableEntityException(AppException):
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InternalServerErrorException(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


# Base business logic exception
class BusinessLogicError(Exception):
    """Base class for business logic exceptions."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# Authentication specific exceptions
class AuthenticationError(BusinessLogicError):
    """Raised when authentication fails."""
    pass


class UserNotFoundError(BusinessLogicError):
    """Raised when user is not found."""
    pass


class InvalidTokenError(BusinessLogicError):
    """Raised when token is invalid."""
    pass


class TokenExpiredError(BusinessLogicError):
    """Raised when token has expired."""
    pass


# Database operation exceptions
class DatabaseOperationError(BusinessLogicError):
    """Raised when database operation fails."""
    pass


class DuplicateResourceError(BusinessLogicError):
    """Raised when trying to create a resource that already exists."""
    pass


# Validation exceptions
class ValidationError(BusinessLogicError):
    """Raised when data validation fails."""
    pass


# Permission exceptions
class PermissionDeniedError(BusinessLogicError):
    """Raised when user lacks required permissions."""
    pass
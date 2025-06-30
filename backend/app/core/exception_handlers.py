"""Global exception handlers for unified error handling."""

import logging
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AuthenticationError, UserNotFoundError, InvalidTokenError, TokenExpiredError,
    AppException
)

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent response format."""
    logger.warning(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(f"App exception on {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "application_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", None)
        },
        headers=exc.headers
    )


async def auth_exception_handler(request: Request, exc: Union[AuthenticationError, InvalidTokenError, TokenExpiredError]) -> JSONResponse:
    """Handle authentication-related exceptions."""
    logger.warning(f"Authentication error on {request.url}: {str(exc)}")
    
    # Map specific auth exceptions to appropriate HTTP status codes
    if isinstance(exc, (InvalidTokenError, TokenExpiredError)):
        status_code = status.HTTP_401_UNAUTHORIZED
        error_type = "invalid_token"
    else:
        status_code = status.HTTP_401_UNAUTHORIZED
        error_type = "authentication_failed"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "message": str(exc) or "Authentication failed",
            "status_code": status_code,
            "request_id": getattr(request.state, "request_id", None)
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundError) -> JSONResponse:
    """Handle user not found exceptions."""
    logger.warning(f"User not found on {request.url}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "user_not_found",
            "message": str(exc) or "User not found",
            "status_code": status.HTTP_404_NOT_FOUND,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database-related exceptions."""
    logger.error(f"Database error on {request.url}: {str(exc)}", exc_info=True)
    
    # Determine specific error type
    if isinstance(exc, IntegrityError):
        status_code = status.HTTP_409_CONFLICT
        error_type = "data_conflict"
        message = "Data integrity constraint violation"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_type = "database_error"
        message = "Database operation failed"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "message": message,
            "status_code": status_code,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the application."""
    
    # Custom application exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(AuthenticationError, auth_exception_handler)
    app.add_exception_handler(InvalidTokenError, auth_exception_handler)
    app.add_exception_handler(TokenExpiredError, auth_exception_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    
    # Database exceptions
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # Standard HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured successfully")
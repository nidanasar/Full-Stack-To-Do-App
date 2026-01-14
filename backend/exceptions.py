"""Custom exceptions and error handlers for consistent API responses."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: ErrorDetail


class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedException(AppException):
    """401 Unauthorized exception."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class NotFoundException(AppException):
    """404 Not Found exception."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictException(AppException):
    """409 Conflict exception."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationException(AppException):
    """422 Validation exception."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def create_error_response(code: str, message: str, status_code: int) -> JSONResponse:
    """Create a standardized error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    return create_error_response(exc.code, exc.message, exc.status_code)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error.get("loc", []))
        message = f"{field}: {first_error.get('msg', 'Validation error')}"
    else:
        message = "Validation error"

    return create_error_response(
        code="VALIDATION_ERROR",
        message=message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

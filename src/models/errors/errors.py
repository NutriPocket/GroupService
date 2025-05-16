from fastapi import HTTPException, status
from typing import Optional


class CustomHTTPException(HTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            kwargs.get("status") or status.HTTP_400_BAD_REQUEST,
            kwargs.get("detail") or ""
        )
        self.title = kwargs.get("title") or "CustomHTTPException"


class ValidationError(CustomHTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            status=kwargs.get("status") or status.HTTP_400_BAD_REQUEST,
            detail=kwargs.get("detail") or "",
            title=kwargs.get("title") or "ValidationError"
        )


class EntityAlreadyExistsError(CustomHTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            status=kwargs.get("status") or status.HTTP_409_CONFLICT,
            detail=kwargs.get("detail") or "",
            title=kwargs.get("title") or "Entity already exists"
        )


class AuthenticationError(CustomHTTPException):
    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status=status.HTTP_401_UNAUTHORIZED,
            detail=detail if detail else "",
            title="AuthenticationError"
        )


class NotFoundError(CustomHTTPException):
    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Entity not found",
            title="NotFoundError"
        )


class ServiceUnavailableError(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
            title="ServiceUnavailableError"
        )

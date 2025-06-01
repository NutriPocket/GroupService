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
            detail=kwargs.get("detail", ""),
            title=kwargs.get("title", "ValidationError")
        )


class ConflictError(CustomHTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            status=kwargs.get("status") or status.HTTP_409_CONFLICT,
            detail=kwargs.get("detail", ""),
            title=kwargs.get("title", "ConflictError")
        )


class EntityAlreadyExistsError(CustomHTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            status=kwargs.get("status") or status.HTTP_409_CONFLICT,
            detail=kwargs.get("detail", ""),
            title=kwargs.get("title", "Entity already exists")
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


class BadGatewayError(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status=status.HTTP_502_BAD_GATEWAY,
            detail="Bad gateway",
            title="BadGatewayError"
        )

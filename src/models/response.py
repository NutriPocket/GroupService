from typing import Generic, TypeVar
from fastapi import Response
from pydantic import BaseModel, Field

T = TypeVar("T")


class CustomResponse(BaseModel, Generic[T]):
    data: T


class ErrorDTO(BaseModel):
    type: str = Field(
        ...,
        description="Type of the error",
        examples=["about:blank"],
        title="Error type",
    )
    title: str = Field(
        ...,
        description="Title of the error",
        examples=["Validation error"],
        title="Error title",
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        examples=[400],
        title="HTTP status code",
    )
    detail: str = Field(
        ...,
        description="Detailed error message",
        examples=["Bad request"],
        title="Error detail",
    )
    instance: str = Field(
        ...,
        description="URL of the request",
        examples=["http://localhost:8000/api/v1/groups"],
        title="Request URL",
    )

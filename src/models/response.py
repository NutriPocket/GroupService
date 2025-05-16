from typing import Generic, TypeVar
from fastapi import Response
from pydantic import BaseModel

T = TypeVar("T")


class CustomResponse(BaseModel, Generic[T]):
    data: T


class ErrorDTO(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CustomResponse(BaseModel, Generic[T]):
    data: T

from typing import Literal, TypedDict, Union


class JwtUserPayload(TypedDict):
    type: Literal['user']
    userId: int
    email: str
    username: str

JwtCustomPayload = JwtUserPayload 

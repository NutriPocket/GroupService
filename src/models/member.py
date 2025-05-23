from datetime import datetime
from pydantic import BaseModel, Field


class Member(BaseModel):
    user_id: str = Field(
        ...,
        description="ID of the member user",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    created_at: datetime = Field(...,
                                 description="Creation timestamp of the routine")


class MemberDTO(BaseModel):
    group_id: str = Field(
        ...,
        description="ID of the group",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    user_id: str = Field(
        ...,
        description="ID of the user",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )

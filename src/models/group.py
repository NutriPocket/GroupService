from datetime import datetime
from pydantic import BaseModel, Field

from models.member import Member
from models.routine import RoutineReturn


class GroupDTO(BaseModel):
    name: str = Field(..., description="Name of the group", min_length=3, max_length=64)
    description: str = Field(..., description="Description of the group", max_length=512)
    owner_id: str = Field(
        ..., 
        description="ID of the group owner",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36, 
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )


class GroupReturn(GroupDTO):
    id: str = Field(
        ..., 
        description="ID of the group", 
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36, 
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    routines: list[RoutineReturn] = Field([], description="List of routines associated with the group")
    created_at: datetime = Field(..., description="Creation timestamp of the group")
    updated_at: datetime = Field(..., description="Last update timestamp of the group")

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from tests.test_jwt import auth_header


class Day(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class PostRoutineParams():
    force_members: bool = False
    auth_header: str = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Schedule(BaseModel):
    day: Day = Field(
        ...,
        description="Day of the week for the routine",
        examples=["Monday", "Tuesday", "Wednesday",
                  "Thursday", "Friday", "Saturday", "Sunday"],
        max_length=10,
        min_length=3,
        pattern="^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$"
    )
    start_hour: int = Field(
        ...,
        ge=0, le=23,
        description="Start hour of the routine",
        examples=[0, 12, 23],
        title="Routine start hour",
    )
    end_hour: int = Field(
        ...,
        ge=0, le=23,
        description="End hour of the routine",
        examples=[1, 13, 24],
        title="Routine end hour",
    )


class RoutineDTO(Schedule):
    name: str = Field(
        ...,
        description="Name of the routine",
        min_length=3, max_length=64,
        examples=["Morning Workout", "Evening Study"]
    )
    description: str = Field(
        ...,
        description="Description of the routine",
        max_length=512,
        examples=["A routine for morning workouts",
                  "A routine for evening study sessions"]
    )
    creator_id: str = Field(
        ...,
        description="ID of the user routine creator",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )


class RoutineReturn(RoutineDTO):
    id: str = Field(
        ...,
        description="ID of the routine",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    group_id: str = Field(
        ...,
        description="ID of the group associated with the routine",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    created_at: datetime = Field(...,
                                 description="Creation timestamp of the routine")
    updated_at: datetime = Field(...,
                                 description="Last update timestamp of the routine")

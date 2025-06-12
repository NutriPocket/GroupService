from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from models.poll import Option, PollDTO, PollReturn


class EventDTO(BaseModel):
    date: datetime = Field(
        ...,
        description="Day of the week for the routine",
        examples=["2002-05-03", "2023-10-01"],
        title="Event date",
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
    poll: Optional[PollDTO | PollReturn] = Field(
        None,
        description="Optional poll associated with the event",
        examples=[
            PollDTO(
                question="What time should we start?",
                options=[
                    Option(
                        id=1, text="9 AM", created_at=datetime.now()
                    ),
                    Option(
                        id=2, text="10 AM", created_at=datetime.now()
                    )
                ]
            )
        ]
    )


class EventReturn(EventDTO):
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

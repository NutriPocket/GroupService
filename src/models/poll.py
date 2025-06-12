from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Option(BaseModel):
    id: int = Field(
        ...,
        description="ID of the option",
        examples=[1, 2, 3],
        title="Option ID",
        ge=1
    )
    text: str = Field(
        ...,
        description="Text of the option",
        examples=["Option 1", "Option 2", "Option 3"],
        max_length=256,
        min_length=1
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Creation timestamp of the option",
        examples=[datetime.now()],
        title="Creation Timestamp"
    )


class PollDTO(BaseModel):
    question: str = Field(
        ...,
        description="Question of the poll",
        examples=["What is your favorite color?", "Do you like Python?"],
        max_length=512,
        min_length=1
    )
    options: list[Option] = Field(
        ...,
        description="List of options for the poll",
        min_length=2,
        max_length=10,
        examples=[
            [
                Option(
                    id=1, text="Red", created_at=datetime.now()
                ),
                Option(
                    id=2, text="Blue", created_at=datetime.now()
                )
            ],
            [
                Option(
                    id=1, text="Yes", created_at=datetime.now()
                ),
                Option(
                    id=2, text="No", created_at=datetime.now()
                )
            ]
        ]
    )


class PollReturn(PollDTO):
    id: str = Field(
        ...,
        description="ID of the user who voted",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="User UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    votes: dict[int, int] = Field(
        default_factory=dict,
        description="Votes for each option in the poll",
        examples=[{1: 10, 2: 5}],
        title="Votes"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp of the poll",
        examples=[datetime.now()],
        title="Creation Timestamp"
    )


class VoteDTO(BaseModel):
    user_id: str = Field(
        ...,
        description="ID of the user who voted",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        title="User UUID",
        min_length=36, max_length=36,
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    option_id: int = Field(
        ...,
        description="ID of the option voted for",
        examples=[1, 2, 3],
        title="Option ID",
        ge=1
    )
    poll_id: str = Field(
        "",
        description="Ignore this parameter, it will be filled with the poll UUID from URI path",
        title="Poll UUID",
    )

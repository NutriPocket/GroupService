from datetime import datetime
from pydantic import BaseModel

from models.member import Member


class GroupDTO(BaseModel):
    name: str
    description: str
    owner_id: str


class GroupReturn(GroupDTO):
    id: str
    created_at: datetime
    updated_at: datetime

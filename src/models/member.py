from datetime import datetime
from pydantic import BaseModel


class Member(BaseModel):
    user_id: str
    created_at: datetime


class MemberDTO(BaseModel):
    group_id: str
    user_id: str

from pydantic import BaseModel


class Member(BaseModel):
    user_id: str


class MemberDTO(BaseModel):
    group_id: str
    user_id: str

from pydantic import BaseModel


class Health(BaseModel):
    health: str


class HealthDB(BaseModel):
    db_health: str

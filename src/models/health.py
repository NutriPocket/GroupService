from pydantic import BaseModel, Field


class Health(BaseModel):
    health: str = Field(
        ...,
        description="Health status of the service",
        examples=["OK", "😎"],
        title="Health Status",
    )


class HealthDB(BaseModel):
    db_health: str = Field(
        ...,
        description="Health status of the service database",
        examples=["OK", "😎"],
        title="Database health status",
    )

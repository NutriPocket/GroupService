from abc import ABCMeta, abstractmethod
from typing import Any, Optional
from sqlalchemy import Engine, Executable, text
from database.database import engine


class IHealthRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_health(self) -> dict[Any, Any]:
        pass


class HealthRepository(IHealthRepository):
    def __init__(self, engine_: Optional[Engine] = None):
        self.engine = engine_ or engine

    def get_health(self) -> dict[Any, Any]:
        with self.engine.connect() as connection:
            query: Executable = text(
                "SELECT 1 as db_health"
            )

            res = connection.execute(query)
            return {key: value for key, value in res.one()._mapping.items()}

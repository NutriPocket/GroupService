from abc import ABCMeta, abstractmethod
from typing import Any, Optional
from sqlalchemy import Engine, Executable, text
from database.database import engine


class IFoodRepository(metaclass=ABCMeta):
    @abstractmethod
    def example(self) -> None:
        pass


class FoodRepository(IFoodRepository):
    def __init__(self, engine_: Optional[Engine] = None):
        self.engine = engine_ or engine
    
    def example(self) -> None:
        pass

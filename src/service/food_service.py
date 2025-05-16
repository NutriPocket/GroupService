from abc import ABCMeta, abstractmethod
from typing import Optional

from repository.food_repository import FoodRepository, IFoodRepository


class IFoodService(metaclass=ABCMeta):
    @abstractmethod
    def example(self) -> None:
        pass


class FoodService(IFoodService):
    def __init__(self, repository: Optional[IFoodRepository] = None):
        self.repository = repository or FoodRepository()

    def example(self) -> None:
        pass

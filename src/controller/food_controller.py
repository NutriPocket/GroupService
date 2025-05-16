from typing import Optional
from fastapi import status
from fastapi.responses import JSONResponse

from service.food_service import FoodService, IFoodService


class FoodController:
    def __init__(self, service: Optional[IFoodService] = None):
        self.service = service or FoodService()

    def example(self) -> None:
        pass

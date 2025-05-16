from fastapi import APIRouter, status

from controller.food_controller import FoodController

router = APIRouter()


@router.get(
    "/",
    summary="Food example",
    status_code=status.HTTP_200_OK
)
def example() -> None:
    return FoodController().example()

from fastapi import APIRouter, status

from controller.health_controller import HealthController
from models.health import Health, HealthDB

router = APIRouter()


@router.get(
    "/",
    summary="Health check",
    status_code=status.HTTP_200_OK
)
def get_health() -> Health:
    return HealthController().get_health()


@router.get(
    "/db",
    summary="Health check db",
    status_code=status.HTTP_200_OK
)
def get_health_db() -> HealthDB:
    return HealthController().get_health_db()

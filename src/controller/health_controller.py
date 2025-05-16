from typing import Optional
from fastapi import status
from fastapi.responses import JSONResponse

from models.health import Health, HealthDB
from service.health_service import HealthService, IHealthService


class HealthController:
    def __init__(self, service: Optional[IHealthService] = None):
        self.service = service or HealthService()

    def get_health(self) -> Health:
        return self.service.get_health()

    def get_health_db(self) -> HealthDB:
        return self.service.get_health_db()

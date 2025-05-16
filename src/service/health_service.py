from abc import ABCMeta, abstractmethod
from typing import Optional

from models.health import Health, HealthDB
from repository.health_repository import HealthRepository, IHealthRepository


class IHealthService(metaclass=ABCMeta):
    @abstractmethod
    def get_health(self) -> Health:
        """
        Get the health status of the service.

        Returns:
            Health: An instance of the Health model with the health status.
        """
        pass

    @abstractmethod
    def get_health_db(self) -> HealthDB:
        """
        Check the health of the database connection.

        Returns:
            HealthDB: An instance of the HealthDB model with the database health status.
        Raises:
            Exception: If the database connection is not healthy.
        """
        pass


class HealthService(IHealthService):
    def __init__(self, repository: Optional[IHealthRepository] = None):
        self.repository = repository or HealthRepository()

    def get_health(self) -> Health:
        """
        Get the health status of the service.

        Returns:
            Health: An instance of the Health model with the health status.
        """
        return Health(health="😎")

    def get_health_db(self) -> HealthDB:
        # If db is not healthy, it will raise an exception
        _ = self.repository.get_health()
        return HealthDB(db_health="😎")

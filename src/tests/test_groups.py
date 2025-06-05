from fastapi.exceptions import RequestValidationError
import pytest
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status

from models.errors.errors import CustomHTTPException
from models.member import Member
from models.routine import Schedule
from repository.group_repository import GroupRepository
from routes.group_routes import router as group_router
from middleware.error_handler import error_handler
from controller.group_controller import GroupController
from database.database import engine
from sqlalchemy import text

from service.group_service import GroupService
app = FastAPI()

app.include_router(group_router, tags=["groups"])


@app.exception_handler(RequestValidationError)
@app.exception_handler(CustomHTTPException)
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_handler(request, exc)

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM groups"))
        conn.execute(text("DELETE FROM group_members"))
        conn.execute(text("DELETE FROM group_routines"))
        conn.execute(text("DELETE FROM group_events"))


class TestGroupRoutes:
    # Test data
    valid_group = {
        "name": "Test Group",
        "description": "Test Group Description",
        "owner_id": "1cdba348-0279-4634-9bcd-c8ea1d2856af"
    }

    valid_group_id = "2cdba348-0279-4634-9bcd-c8ea1d2856af"
    invalid_group_id = "invalid_group_id"
    not_found_group_id = "3cdba348-0279-4634-9bcd-c8ea1d2856af"
    valid_user_id = "1cdba348-0279-4634-9bcd-c8ea1d2856af"
    another_valid_user_id = "2cdba348-0279-4634-9bcd-c8ea1d2856af"
    invalid_user_id = "invalid_user_id"
    valid_event_id = "4cdba348-0279-4634-9bcd-c8ea1d2856af"
    not_found_event_id = "5cdba348-0279-4634-9bcd-c8ea1d2856af"
    invalid_event_id = "invalid_event_id"

    valid_event = {
        "name": "Team Meeting",
        "description": "Weekly team status meeting",
        "date": "2025-07-15T00:00:00",
        "start_hour": 10,
        "end_hour": 12,
        "creator_id": "1cdba348-0279-4634-9bcd-c8ea1d2856af"
    }

    """
        POST /groups
    """

    def test_create_group_success(self):
        response = client.post("/groups", json=self.valid_group)
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert response.json()["data"]["name"] == self.valid_group["name"]

    def test_create_group_with_blank_fields(self):
        blank_request = self.valid_group.copy()
        blank_request["name"] = ""
        blank_request["description"] = ""
        blank_request["owner_id"] = ""
        response = client.post("/groups", json=blank_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "name: String should have at least 3 characters, got '' & owner_id: String should have at least 36 characters, got ''"

    def test_create_group_with_invalid_owner_uuid(self):
        bad_uuid_owner_id = self.valid_group.copy()
        bad_uuid_owner_id["owner_id"] = "bad-uuid"
        response = client.post("/groups", json=bad_uuid_owner_id)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "owner_id: String should have at least 36 characters, got 'bad-uuid'"

    def test_create_invalid_group(self):
        invalid_group = {
            # Missing required fields
            "name": "Test Group"
            # missing owner_id
        }
        response = client.post("/groups", json=invalid_group)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_group_server_error(self, monkeypatch):
        # Monkeypatch to simulate 500 from controller
        def mock_post_group_error(self, group):
            raise Exception("Database connection error")

        monkeypatch.setattr(GroupController, "post_group",
                            mock_post_group_error)

        with pytest.raises(Exception):
            client.post("/groups", json=self.valid_group)

    """
        GET /groups/{group_id}
    """

    def test_get_group_success(self, monkeypatch):
        # Monkeypatch the database response for a predefined group ID
        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        response = client.get(f"/groups/{group_id}")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert response.json()["data"]["id"] == group_id

    def test_get_group_with_bad_uuid(self):
        response = client.get(f"/groups/{self.invalid_group_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "group_id: String should have at least 36 characters, got 'invalid_group_id'"

    def test_get_nonexistent_group(self):
        response = client.get(f"/groups/{self.not_found_group_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    """
        GET /users/{user_id}/groups
    """

    def test_get_empty_user_groups_success(self):
        response = client.get(f"/users/{self.valid_user_id}/groups")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) == 0

    def test_get_user_groups(self):
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        client.post(
            f"/groups/{group_id}/users/{self.valid_user_id}")

        response = client.get(f"/users/{self.valid_user_id}/groups")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0
        assert response.json()["data"][0]["id"] == group_id

    def test_get_user_groups_bad_uuid(self):
        response = client.get(f"/users/{self.invalid_user_id}/groups")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "user_id: String should have at least 36 characters, got 'invalid_user_id'"

    def test_get_user_groups_server_error(self, monkeypatch):
        # Monkeypatch to simulate 500 from controller

        def mock_get_user_groups_error(self, user_id):
            raise Exception("Database query error")

        monkeypatch.setattr(GroupController, "get_user_groups",
                            mock_get_user_groups_error)

        with pytest.raises(Exception):
            client.get(f"/users/{self.valid_user_id}/groups")

    """
        POST /groups/{group_id}/users
    """

    def test_add_member_to_group_success(self, monkeypatch):
        # Monkeypatch the database response
        def mock_post_member(self, group_id, user_id):
            return {"data": [{"user_id": user_id, "group_id": group_id, "created_at": "2023-01-01T00:00:00"}]}

        monkeypatch.setattr(GroupController, "post_member", mock_post_member)

        response = client.post(
            f"/groups/{self.valid_group_id}/users/{self.valid_user_id}")
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0

    def test_add_member_to_group_with_bad_uuid(self):
        response = client.post(
            f"/groups/{self.invalid_group_id}/users/{self.valid_user_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "group_id: String should have at least 36 characters, got 'invalid_group_id'"

    def test_add_member_to_non_existent_group(self):
        response = client.post(
            f"/groups/{self.not_found_group_id}/users/{self.valid_user_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    def test_add_member_to_group_with_bad_user_uuid(self):
        response = client.post(
            f"/groups/{self.valid_group_id}/users/{self.invalid_user_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "user_id: String should have at least 36 characters, got 'invalid_user_id'"

    def test_add_member_to_bad_uuid_group(self):
        response = client.post(
            f"/groups/{self.invalid_group_id}/users/{self.valid_user_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    """
        GET /groups/{group_id}/users/
    """

    def test_get_group_members_success(self, monkeypatch):
        # Monkeypatch the database response
        user_id = self.valid_user_id

        def mock_get_group_members(self, group_id):
            return {"data": [{"user_id": user_id, "group_id": group_id, "created_at": "2023-01-01T00:00:00"}]}

        monkeypatch.setattr(
            GroupController, "get_group_members", mock_get_group_members)

        response = client.get(f"/groups/{self.valid_group_id}/users")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0

    def test_get_group_members_with_bad_uuid(self):
        response = client.get(
            f"/groups/{self.invalid_group_id}/users/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "group_id: String should have at least 36 characters, got 'invalid_group_id'"

    def test_get_group_members_server_error(self, monkeypatch):
        # Monkeypatch to simulate 500 from controller
        def mock_get_group_members_error(self, group_id):
            raise Exception("Database query error")

        monkeypatch.setattr(GroupController, "get_group_members",
                            mock_get_group_members_error)

        with pytest.raises(Exception):
            client.get(f"/groups/{self.valid_group_id}/users")

    def test_get_group_members_not_found(self):
        response = client.get(
            f"/groups/{self.not_found_group_id}/users/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    """
        POST /groups/{group_id}/routines/
    """

    def test_post_group_routine_success(self, monkeypatch):
        def mock_free_schedules(self, members: list[Member], auth_header: str) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=8,
                    end_hour=15,
                ),
            ]

        monkeypatch.setattr(
            GroupService, "get_free_schedules", mock_free_schedules)

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=true", json=routine)
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0
        assert response.json()["data"][0]["name"] == routine["name"]
        assert response.json()[
            "data"][0]["description"] == routine["description"]
        assert response.json()["data"][0]["day"] == routine["day"]
        assert response.json()[
            "data"][0]["start_hour"] == routine["start_hour"]
        assert response.json()["data"][0]["end_hour"] == routine["end_hour"]
        assert response.json()["data"][0]["group_id"] == group_id
        assert response.json()["data"][0]["id"] is not None
        assert response.json()["data"][0]["created_at"] is not None
        assert response.json()["data"][0]["updated_at"] is not None

    def test_post_group_routine_with_user_schedules_colision(self, monkeypatch):
        def mock_free_schedules(self, members: list[Member], auth_header: str) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=9,
                    end_hour=10,
                ),
            ]

        monkeypatch.setattr(
            GroupService, "get_free_schedules", mock_free_schedules)

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 8,
            "end_hour": 11,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=false", json=routine)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "There are members with conflicting routines" == response.json()[
            "detail"]
        assert "Conflict in routine schedules" == response.json()["title"]
        assert "about:blank" == response.json()["type"]
        assert 409 == response.json()["status"]

    def test_post_group_routine_without_user_schedules_colision(self, monkeypatch):
        def mock_free_schedules(self, members: list[Member], auth_header: str) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=8,
                    end_hour=15,
                ),
            ]

        monkeypatch.setattr(
            GroupService, "get_free_schedules", mock_free_schedules)

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=false", json=routine)
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0

    def test_post_group_routine_with_user_groups_schedules_collision(self, monkeypatch):
        def mock_get_user_groups_routines_schedules(self, members: list[Member]) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=9,
                    end_hour=10,
                ),
            ]

        monkeypatch.setattr(
            GroupRepository, "get_user_groups_routines_schedules", mock_get_user_groups_routines_schedules
        )

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=false", json=routine)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert f"Conflicting member routine on Monday from 9 to 10" == response.json()[
            "detail"]
        assert "Conflict in routine schedules" == response.json()[
            "title"]
        assert "about:blank" == response.json()["type"]
        assert 409 == response.json()["status"]

    def test_post_group_routine_without_user_groups_schedules_collision(self, monkeypatch):
        def mock_get_user_groups_routines_schedules(self, members: list[Member]) -> list[Schedule]:
            return []

        monkeypatch.setattr(
            GroupRepository, "get_user_groups_routines_schedules", mock_get_user_groups_routines_schedules
        )

        def mock_free_schedules(self, members: list[Member], auth_header: str) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=8,
                    end_hour=15,
                ),
            ]

        monkeypatch.setattr(
            GroupService, "get_free_schedules", mock_free_schedules)

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=false", json=routine)
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0

    def test_post_routine_without_being_a_member(self):
        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.another_valid_user_id
        }

        response = client.post(
            f"/groups/{group_id}/routines?force_members=false", json=routine)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert f"User with id {self.another_valid_user_id} is not a member of group {group_id}" == response.json()[
            "detail"]
        assert "AuthenticationError" == response.json()["title"]

    def test_post_group_routine_with_bad_uuid(self):
        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{self.invalid_group_id}/routines", json=routine)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "group_id: String should have at least 36 characters, got 'invalid_group_id'"

    def test_post_group_routine_not_found(self):
        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        response = client.post(
            f"/groups/{self.not_found_group_id}/routines", json=routine)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    """
        GET /groups/{group_id}/routines/
    """

    def test_get_group_routines_empty(self):
        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        response = client.get(f"/groups/{group_id}/routines")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) == 0
        assert response.json()["data"] == []

    def test_get_group_routines_success(self, monkeypatch):
        def mock_free_schedules(self, members: list[Member], auth_header: str) -> list[Schedule]:
            return [
                Schedule(
                    day="Monday",  # type: ignore
                    start_hour=8,
                    end_hour=15,
                ),
            ]

        monkeypatch.setattr(
            GroupService, "get_free_schedules", mock_free_schedules)

        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10,
            "creator_id": self.valid_user_id
        }

        client.post(
            f"/groups/{group_id}/routines", json=routine)

        response = client.get(f"/groups/{group_id}/routines")
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) > 0
        assert response.json()["data"][0]["name"] == routine["name"]
        assert response.json()[
            "data"][0]["description"] == routine["description"]
        assert response.json()["data"][0]["day"] == routine["day"]
        assert response.json()[
            "data"][0]["start_hour"] == routine["start_hour"]
        assert response.json()["data"][0]["end_hour"] == routine["end_hour"]
        assert response.json()["data"][0]["group_id"] == group_id
        assert response.json()["data"][0]["id"] is not None
        assert response.json()["data"][0]["created_at"] is not None
        assert response.json()["data"][0]["updated_at"] is not None

    def test_get_group_routines_with_bad_uuid(self):
        response = client.get(
            f"/groups/{self.invalid_group_id}/routines/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == "group_id: String should have at least 36 characters, got 'invalid_group_id'"

    def test_get_group_routines_not_found(self):
        response = client.get(
            f"/groups/{self.not_found_group_id}/routines/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    """
        POST /groups/{group_id}/events
    """

    def test_create_event_success(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)

        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert response.json()["data"]["name"] == self.valid_event["name"]
        assert response.json()[
            "data"]["description"] == self.valid_event["description"]
        assert response.json()["data"]["group_id"] == group_id
        assert response.json()[
            "data"]["creator_id"] == self.valid_event["creator_id"]
        assert response.json()["data"]["id"] is not None
        assert response.json()["data"]["created_at"] is not None
        assert response.json()["data"]["updated_at"] is not None

    def test_create_event_with_date_in_past(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a date in the past
        event = self.valid_event.copy()
        event["date"] = "2020-01-01T00:00:00"
        response = client.post(f"/groups/{group_id}/events", json=event)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()[
            "detail"] == "Event date cannot be in the past"

    def test_create_event_with_invalid_group_id(self):
        response = client.post(
            f"/groups/{self.invalid_group_id}/events", json=self.valid_event)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == f"group_id: String should have at least 36 characters, got '{self.invalid_group_id}'"

    def test_create_event_group_not_found(self):
        response = client.post(
            f"/groups/{self.not_found_group_id}/events", json=self.valid_event)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    def test_create_event_user_not_member(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Try to create an event with a user who isn't a member
        event = self.valid_event.copy()
        event["creator_id"] = self.another_valid_user_id

        response = client.post(f"/groups/{group_id}/events", json=event)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()[
            "detail"] == f"User with id {self.another_valid_user_id} is not a member of group {group_id}"

    def test_create_event_with_collision(self, monkeypatch):
        # Mock the repository to simulate a collision
        def mock_find_colliding_events(self, group_id, date, start_hour, end_hour):
            return [{"id": "test-id", "name": "Existing Event"}]

        monkeypatch.setattr(
            GroupRepository, "find_group_colliding_events", mock_find_colliding_events)

        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Try to create an event that collides
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Conflict in event schedules" == response.json()["title"]
        assert "Event collides with existing events:" in response.json()[
            "detail"]

    """
        GET /groups/{group_id}/events
    """

    def test_get_group_events_empty(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Get events (should be empty)
        response = client.get(f"/groups/{group_id}/events")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) == 0

    def test_get_group_events_success(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        client.post(f"/groups/{group_id}/events", json=self.valid_event)

        # Get all events
        response = client.get(f"/groups/{group_id}/events")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["name"] == self.valid_event["name"]
        assert response.json()[
            "data"][0]["description"] == self.valid_event["description"]

    def test_get_group_events_with_invalid_group_id(self):
        response = client.get(f"/groups/{self.invalid_group_id}/events")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()[
            "detail"] == f"group_id: String should have at least 36 characters, got '{self.invalid_group_id}'"

    def test_get_group_events_group_not_found(self):
        response = client.get(f"/groups/{self.not_found_group_id}/events")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()[
            "detail"] == f"Group with id {self.not_found_group_id} not found"

    """
        GET /groups/{group_id}/events/{event_id}
    """

    def test_get_group_event_success(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Get the specific event
        response = client.get(f"/groups/{group_id}/events/{event_id}")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert response.json()["data"]["id"] == event_id
        assert response.json()["data"]["name"] == self.valid_event["name"]

    def test_get_group_event_with_invalid_ids(self):
        response = client.get(
            f"/groups/{self.invalid_group_id}/events/{self.valid_event_id}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "group_id: String should have at least 36 characters" in response.json()[
            "detail"]

        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.get(
            f"/groups/{group_id}/events/{self.invalid_event_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "event_id: String should have at least 36 characters" in response.json()[
            "detail"]

    def test_get_group_event_not_found(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.get(
            f"/groups/{group_id}/events/{self.not_found_event_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Event with id {self.not_found_event_id} not found in group {group_id}" in response.json()[
            "detail"]

    """
        PATCH /groups/{group_id}/events/{event_id}
    """

    def test_update_event_success(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Update the event
        updated_event = self.valid_event.copy()
        updated_event["name"] = "Updated Meeting"
        updated_event["description"] = "Updated description"

        response = client.patch(
            f"/groups/{group_id}/events/{event_id}", json=updated_event)

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert response.json()["data"]["id"] == event_id
        assert response.json()["data"]["name"] == "Updated Meeting"
        assert response.json()["data"]["description"] == "Updated description"

    def test_update_event_with_date_in_past(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Update the event with a date in the past
        updated_event = self.valid_event.copy()
        updated_event["date"] = "2020-01-01T00:00:00"

        response = client.patch(
            f"/groups/{group_id}/events/{event_id}", json=updated_event)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()[
            "detail"] == "Event date cannot be in the past"

    def test_update_event_with_invalid_ids(self):
        response = client.patch(
            f"/groups/{self.invalid_group_id}/events/{self.valid_event_id}", json=self.valid_event)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.patch(
            f"/groups/{group_id}/events/{self.invalid_event_id}", json=self.valid_event)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_event_not_found(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.patch(
            f"/groups/{group_id}/events/{self.not_found_event_id}", json=self.valid_event)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Event with id {self.not_found_event_id} not found in group {group_id}" in response.json()[
            "detail"]

    def test_update_event_user_not_member(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Update with non-member user
        updated_event = self.valid_event.copy()
        updated_event["creator_id"] = self.another_valid_user_id

        response = client.patch(
            f"/groups/{group_id}/events/{event_id}", json=updated_event)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert f"User with id {self.another_valid_user_id} is not a member of group {group_id}" in response.json()[
            "detail"]

    """
        DELETE /groups/{group_id}/events/{event_id}
    """

    def test_delete_event_success(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event for the group
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Delete the event
        response = client.delete(f"/groups/{group_id}/events/{event_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] is None

        # Verify event is gone
        response = client.get(f"/groups/{group_id}/events/{event_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_event_with_invalid_ids(self):
        response = client.delete(
            f"/groups/{self.invalid_group_id}/events/{self.valid_event_id}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.delete(
            f"/groups/{group_id}/events/{self.invalid_event_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_event_not_found(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        response = client.delete(
            f"/groups/{group_id}/events/{self.not_found_event_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Event with id {self.not_found_event_id} not found in group {group_id}" in response.json()[
            "detail"]

    def test_delete_event_group_not_found(self):
        response = client.delete(
            f"/groups/{self.not_found_group_id}/events/{self.valid_event_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Group with id {self.not_found_group_id} not found" in response.json()[
            "detail"]

    """
        Error cases and edge cases
    """

    def test_create_event_server_error(self, monkeypatch):
        # Monkeypatch to simulate 500 from controller
        def mock_post_event_error(self, group_id, event):
            raise Exception("Database connection error")

        monkeypatch.setattr(
            GroupController, "post_group_event", mock_post_event_error)

        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        with pytest.raises(Exception):
            client.post(f"/groups/{group_id}/events", json=self.valid_event)

    def test_create_event_with_invalid_data(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Invalid date format
        invalid_event = self.valid_event.copy()
        invalid_event["date"] = "not-a-date"
        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid hours
        invalid_event = self.valid_event.copy()
        invalid_event["start_hour"] = 25  # Out of range
        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        invalid_event = self.valid_event.copy()
        invalid_event["end_hour"] = -1  # Out of range
        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing required fields
        invalid_event = {
            "name": "Test Event"
            # Missing required fields
        }
        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

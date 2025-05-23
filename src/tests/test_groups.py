from fastapi.exceptions import RequestValidationError
import pytest
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status

from repository.group_repository import GroupRepository
from routes.group_routes import router as group_router
from middleware.error_handler import error_handler
from controller.group_controller import GroupController
from database.database import engine
from sqlalchemy import text
app = FastAPI()

app.include_router(group_router, tags=["groups"])


@app.exception_handler(RequestValidationError)
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
    invalid_user_id = "invalid_user_id"

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

    def test_post_group_routine_success(self):
        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10
        }

        response = client.post(
            f"/groups/{group_id}/routines", json=routine)
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

    def test_post_group_routine_with_bad_uuid(self):
        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10
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
            "end_hour": 10
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

    def test_get_group_routines_success(self):
        response = client.post("/groups", json=self.valid_group)

        group_id = response.json()["data"]["id"]

        routine = {
            "name": "Test Routine",
            "description": "Test Routine Description",
            "day": "Monday",
            "start_hour": 9,
            "end_hour": 10
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

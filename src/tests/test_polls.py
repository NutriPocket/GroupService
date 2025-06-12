from fastapi.exceptions import RequestValidationError
import pytest
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status
import datetime

from models.errors.errors import CustomHTTPException
from models.member import Member
from models.poll import Option, PollDTO
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
        conn.execute(text("DELETE FROM poll_votes"))
        conn.execute(text("DELETE FROM poll_options"))
        conn.execute(text("DELETE FROM poll"))
        conn.execute(text("DELETE FROM group_events"))
        conn.execute(text("DELETE FROM group_routines"))
        conn.execute(text("DELETE FROM group_members"))
        conn.execute(text("DELETE FROM groups"))


class TestPollRoutes:
    # Test data
    valid_group = {
        "name": "Test Group",
        "description": "Test Group Description",
        "owner_id": "1cdba348-0279-4634-9bcd-c8ea1d2856af"
    }

    valid_user_id = "1cdba348-0279-4634-9bcd-c8ea1d2856af"
    another_valid_user_id = "2cdba348-0279-4634-9bcd-c8ea1d2856af"
    third_valid_user_id = "3cdba348-0279-4634-9bcd-c8ea1d2856af"
    invalid_user_id = "invalid_user_id"
    not_found_poll_id = "5cdba348-0279-4634-9bcd-c8ea1d2856af"
    invalid_poll_id = "invalid_poll_id"

    valid_event = {
        "name": "Team Meeting",
        "description": "Weekly team status meeting",
        "date": "2025-07-15T00:00:00",
        "start_hour": 10,
        "end_hour": 12,
        "creator_id": "1cdba348-0279-4634-9bcd-c8ea1d2856af",
        "poll": {
            "question": "What topic should we focus on?",
            "options": [
                {"id": 1, "text": "Project Status"},
                {"id": 2, "text": "Technical Challenges"},
                {"id": 3, "text": "Future Planning"}
            ]
        }
    }

    valid_vote = {
        "user_id": "1cdba348-0279-4634-9bcd-c8ea1d2856af",
        "option_id": 1
    }

    """
        Test creating an event with a poll
    """

    def test_create_event_with_poll(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)

        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.json()
        assert "poll" in response.json()["data"]
        assert response.json()[
            "data"]["poll"]["question"] == self.valid_event["poll"]["question"]

        # Verify poll has options
        poll = response.json()["data"]["poll"]
        assert len(poll["options"]) == 3
        assert poll["options"][0]["text"] == "Project Status"
        assert poll["options"][1]["text"] == "Technical Challenges"
        assert poll["options"][2]["text"] == "Future Planning"

        # Verify votes are empty initially
        assert poll["votes"] == {}

    """
        Test getting an event with its poll
    """

    def test_get_event_with_poll(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]

        # Get the event with its poll
        response = client.get(f"/groups/{group_id}/events/{event_id}")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert "poll" in response.json()["data"]
        assert response.json()[
            "data"]["poll"]["question"] == self.valid_event["poll"]["question"]

        # Verify poll has options
        poll = response.json()["data"]["poll"]
        assert len(poll["options"]) == 3

    """
        Test voting on a poll
    """

    def test_vote_on_poll(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        poll_id = response.json()["data"]["poll"]["id"]

        # Submit a vote
        vote = self.valid_vote.copy()
        response = client.put(f"/polls/{poll_id}", json=vote)

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert "votes" in response.json()["data"]
        assert response.json()["data"]["votes"] == {"1": 1}

    """
        Test getting poll vote counts
    """

    def test_get_poll_vote_counts(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Add another member to the group
        client.post(f"/groups/{group_id}/users/{self.another_valid_user_id}")

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        event_id = response.json()["data"]["id"]
        poll_id = response.json()["data"]["poll"]["id"]

        # Submit votes from different users
        vote1 = self.valid_vote.copy()
        client.put(f"/polls/{poll_id}", json=vote1)

        vote2 = self.valid_vote.copy()
        vote2["user_id"] = self.another_valid_user_id
        vote2["option_id"] = 2
        client.put(f"/polls/{poll_id}", json=vote2)

        # Get the event with its poll to check votes
        response = client.get(f"/groups/{group_id}/events/{event_id}")

        assert response.status_code == status.HTTP_200_OK
        poll = response.json()["data"]["poll"]
        assert poll["votes"] == {"1": 1, "2": 1}

    """
        Test changing a vote
    """

    def test_change_vote(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        poll_id = response.json()["data"]["poll"]["id"]

        # Submit initial vote
        vote = self.valid_vote.copy()
        client.put(f"/polls/{poll_id}", json=vote)

        # Change vote to another option
        vote["option_id"] = 3
        response = client.put(f"/polls/{poll_id}", json=vote)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["votes"] == {"3": 1}

    """
        Test multiple users voting
    """

    def test_multiple_users_voting(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Add more members to the group
        client.post(f"/groups/{group_id}/users/{self.another_valid_user_id}")
        client.post(f"/groups/{group_id}/users/{self.third_valid_user_id}")

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        poll_id = response.json()["data"]["poll"]["id"]

        # Submit votes from different users
        vote1 = {"user_id": self.valid_user_id, "option_id": 1}
        client.put(f"/polls/{poll_id}", json=vote1)

        vote2 = {"user_id": self.another_valid_user_id, "option_id": 2}
        client.put(f"/polls/{poll_id}", json=vote2)

        vote3 = {"user_id": self.third_valid_user_id, "option_id": 1}
        response = client.put(f"/polls/{poll_id}", json=vote3)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["votes"] == {"1": 2, "2": 1}

    """
        Error cases
    """

    def test_vote_invalid_poll_id(self):
        response = client.put(
            f"/polls/{self.invalid_poll_id}", json=self.valid_vote)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "poll_id: String should have at least 36 characters" in response.json()[
            "detail"]

    def test_vote_nonexistent_poll(self):
        response = client.put(
            f"/polls/{self.not_found_poll_id}", json=self.valid_vote)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Poll with id {self.not_found_poll_id} not found" in response.json()[
            "detail"]

    def test_vote_invalid_option(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        poll_id = response.json()["data"]["poll"]["id"]

        # Try to vote with an invalid option ID
        invalid_vote = self.valid_vote.copy()
        invalid_vote["option_id"] = 99  # Option doesn't exist

        response = client.put(f"/polls/{poll_id}", json=invalid_vote)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Option with id {invalid_vote['option_id']} does not exist in poll {poll_id}" in response.json()[
            "detail"]

    def test_vote_with_invalid_user(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with a poll
        response = client.post(
            f"/groups/{group_id}/events", json=self.valid_event)
        poll_id = response.json()["data"]["poll"]["id"]

        # Try to vote with an invalid user ID format
        invalid_vote = self.valid_vote.copy()
        invalid_vote["user_id"] = self.invalid_user_id

        response = client.put(f"/polls/{poll_id}", json=invalid_vote)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "user_id: String should have at least 36 characters" in response.json()[
            "detail"]

    def test_create_event_with_invalid_poll(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with invalid poll (no options)
        invalid_event = self.valid_event.copy()
        invalid_event["poll"] = {"question": "Invalid poll without options"}

        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "options" in response.json()["detail"]

        # Create an event with invalid poll (only one option)
        invalid_event = self.valid_event.copy()
        invalid_event["poll"] = {
            "question": "Invalid poll with only one option",
            "options": [{"id": 1, "text": "Only option"}]
        }

        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "options" in response.json()["detail"]

    def test_create_event_with_duplicate_option_ids(self):
        # Create a group first
        response = client.post("/groups", json=self.valid_group)
        group_id = response.json()["data"]["id"]

        # Create an event with duplicate option IDs
        invalid_event = self.valid_event.copy()
        invalid_event["poll"] = {
            "question": "Poll with duplicate option IDs",
            "options": [
                {"id": 1, "text": "Option 1"},
                {"id": 1, "text": "Option 2"}  # Same ID as first option
            ]
        }

        response = client.post(
            f"/groups/{group_id}/events", json=invalid_event)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert f"Duplicate option in poll data" in response.json()[
            "detail"]

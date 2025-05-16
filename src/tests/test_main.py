# test_chat_routes.py
from os import getenv
from typing import Any, Coroutine, Optional, Union
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request

import requests_mock
from routes.health_routes import router

from middleware.auth_middleware import JWTMiddleware
from middleware.error_handler import error_handler
from starlette.middleware.base import BaseHTTPMiddleware
from service.jwt_service import JWTService
from models.jwt import JwtCustomPayload


class MockJWTService(JWTService):
    def __init__(self):
        pass

    def sign(self, payload: JwtCustomPayload) -> str:
        return "test-token"

    def verify(self, token: str) -> Union[dict, str]:
        return {
            "userId": 1, "username": "test", 'email': "test@gmail.com", "type": "user"
        }

    def decode(self, token: str) -> Optional[Union[dict, str]]:
        return {
            "userId": 1, "username": "test", 'email': "test@gmail.com", "type": "user"
        }


class MockHTTPBearer(HTTPBearer):
    def __init__(self):
        pass

    async def __call__(  # type: ignore
        self, request: Request
    ) -> Coroutine[Any, Any, HTTPAuthorizationCredentials | None]:
        return HTTPAuthorizationCredentials(
            # type: ignore
            scheme="Bearer", credentials="test-token"
        )


@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer dummy-token"}


@pytest.fixture
def sample_chat_data():
    return {
        "user1": {"id": 1, "username": "test1"},
        "user2": {"id": 2, "username": "test2"}
    }


@pytest.fixture
def sample_message_data():
    return {
        "content": "Hello, World!"
    }


app = FastAPI()

app.add_middleware(BaseHTTPMiddleware,
                   dispatch=JWTMiddleware(MockJWTService(), MockHTTPBearer()))


app.include_router(router, prefix="/health", tags=["health"])


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_handler(request, exc)


client = TestClient(app)


class TestHealthRoutes:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"health": ":)"}


class TestAuthentication:
    def test_invalid_auth_user_username(self):
        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client.post(
                    "/chats/test-chat-id",
                    json={"content": "Hello"}
                )

                data = response.json()

                assert response.status_code == 400
                assert data.detail == "Invalid username provided"
                assert data.title == "Invalid username"

    def test_auth_user_blocked(self):
        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client.post(
                    "/chats/test-chat-id",
                    json={"content": "Hello"}
                )

                data = response.json()

                assert response.status_code == 403
                assert data.detail == "Blocked error"
                assert data.title == "User blocked"

    def test_auth_user_unauthorized(self):
        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client.post(
                    "/chats/test-chat-id",
                    json={"content": "Hello"}
                )

                data = response.json()

                assert response.status_code == 401
                assert data.detail == ""
                assert data.title == "AuthenticationError"

    def test_auth_user_not_found(self):
        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client.post(
                    "/chats/test-chat-id",
                    json={"content": "Hello"}
                )

                data = response.json()

                assert response.status_code == 404
                assert data.detail == "username test not found"
                assert data.title == "NotFoundError"

    def test_service_unavailable(self):
        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client.post(
                    "/chats/test-chat-id",
                    json={"content": "Hello"}
                )

                data = response.json()

                assert response.status_code == 500
                assert data.detail == "Service unavailable"
                assert data.title == "ServiceUnavailableError"

    def test_no_token(self):
        class MockHTTPBearer(HTTPBearer):
            def __init__(self):
                pass

            async def __call__(  # type: ignore
                self, request: Request
            ) -> Coroutine[Any, Any, HTTPAuthorizationCredentials | None]:
                return None  # type: ignore

        app_aux = FastAPI()

        app_aux.add_middleware(BaseHTTPMiddleware,
                               dispatch=JWTMiddleware(MockJWTService(), MockHTTPBearer()))

        app_aux.include_router(router, prefix="/health", tags=["health"])

        @app_aux.exception_handler(Exception)
        async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
            return error_handler(request, exc)

        client_aux = TestClient(app_aux)

        with requests_mock.Mocker() as m:
            with pytest.raises(Exception):
                response = client_aux.get(
                    "/health"
                )

                data = response.json()

                assert response.status_code == 401
                assert data.detail == ""
                assert data.title == "AuthenticationError"

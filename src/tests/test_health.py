from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request

from routes.health_routes import router

from middleware.error_handler import error_handler


app = FastAPI()

app.include_router(router, prefix="/health", tags=["health"])


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_handler(request, exc)


client = TestClient(app)


class TestHealthRoutes:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"health": "😎"}

    def test_health_check_db(self):
        response = client.get("/health/db")
        assert response.status_code == 200
        assert response.json() == {"db_health": "😎"}

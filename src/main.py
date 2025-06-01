import logging
from os import getenv
import os
import dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from middleware.auth_middleware import JWTMiddleware
from middleware.error_handler import error_handler
from starlette.middleware.base import BaseHTTPMiddleware

from routes import group_routes, health_routes

app = FastAPI()


@app.exception_handler(RequestValidationError)
@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_handler(request, exc)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=JWTMiddleware())


app.include_router(health_routes.router, prefix="/health", tags=["health"])
app.include_router(group_routes.router, tags=["groups"])


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s - %(asctime)s', filename='logs.log')

    env_path: str = getenv("ENV_PATH", "../.env")
    env_path = os.path.abspath(env_path)
    print(f"Loading environment variables from {env_path}")
    dotenv.load_dotenv(env_path, override=True, verbose=True)

    HOST: str = getenv("HOST", "0.0.0.0")
    PORT: int = int(getenv("PORT", 8083))

    uvicorn.run(app, host=HOST, port=PORT)

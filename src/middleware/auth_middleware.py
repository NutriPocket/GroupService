from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.errors.errors import AuthenticationError
from service.jwt_service import JWTService


class JWTMiddleware:
    def __init__(self, jwt_service: JWTService | None = None, security: HTTPBearer | None = None):
        self.jwt_service = jwt_service or JWTService()
        self.security = security or HTTPBearer()
        self.__public_routes = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

    async def __call__(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.method == "REDIRECT":
            response = await call_next(request)
            return response

        if request.url.path == "/":
            response = await call_next(request)
            return response

        referer: str = request.headers.get("referer", "")
        if referer and (referer.startswith("http://127.0.0.1:") or referer.startswith("http://localhost:")) and referer.endswith("docs"):
            response = await call_next(request)
            return response

        for route in self.__public_routes:
            if request.url.path.startswith(route):
                response = await call_next(request)
                return response

        if request.url.path == "/":
            response = await call_next(request)
            return response

        credentials: HTTPAuthorizationCredentials | None = await self.security(request)

        if not credentials:
            raise AuthenticationError()

        token = credentials.credentials
        payload = self.jwt_service.verify(token)

        request.state.user = payload
        response = await call_next(request)
        return response

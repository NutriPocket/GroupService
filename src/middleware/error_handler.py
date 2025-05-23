import logging
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from models.errors.errors import CustomHTTPException
from models.response import ErrorDTO


def error_handler(request: Request, e: Exception) -> JSONResponse:
    match e:
        case RequestValidationError():
            content = ErrorDTO(
                type="about:blank",
                title="Validation error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=" & ".join(
                    [f"{err['loc'][1]}: {err['msg']}, got \'{err['input']}\'" for err in e.errors()]),
                instance=str(request.url)
            )

            logging.error(str(content))

            return JSONResponse(
                dict(content),
                status_code=content.status
            )

        case CustomHTTPException():
            content = ErrorDTO(
                type="about:blank",
                title=e.title,
                status=e.status_code,
                detail=e.detail,
                instance=str(request.url)
            )

            logging.error(str(content))

            return JSONResponse(
                content=dict(content),
                status_code=content.status
            )

        case HTTPException():
            content = ErrorDTO(
                type="about:blank",
                title='',
                status=e.status_code,
                detail=e.detail,
                instance=str(request.url)
            )

            logging.error(str(content))

            return JSONResponse(
                dict(content),
                status_code=content.status
            )

        case _:
            content = ErrorDTO(
                type="about:blank",
                title="Internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
                instance=str(request.url)
            )

            logging.error(str(content))

            return JSONResponse(
                dict(content),
                status_code=content.status
            )

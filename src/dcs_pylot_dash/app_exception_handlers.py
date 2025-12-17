# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from starlette.requests import Request
from starlette.responses import Response

from dcs_pylot_dash.exceptions import DCSPylotDashInvalidInputException, DCSPylotDashResourceNotFoundException


class AppExceptionHandlers:

    @staticmethod
    def add_exception_handlers(app: FastAPI) -> None:

        @app.exception_handler(DCSPylotDashInvalidInputException)
        async def default(request: Request, exc: DCSPylotDashInvalidInputException) -> Response:
            http_exc: HTTPException = HTTPException(HTTPStatus.BAD_REQUEST)
            return await http_exception_handler(request, http_exc)

        @app.exception_handler(DCSPylotDashResourceNotFoundException)
        async def default(request: Request, exc: DCSPylotDashResourceNotFoundException) -> Response:
            http_exc: HTTPException = HTTPException(HTTPStatus.NOT_FOUND)
            return await http_exception_handler(request, http_exc)

        @app.exception_handler(Exception)
        async def default(request: Request, exc: Exception) -> Response:
            http_exc: HTTPException = HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR)
            return await http_exception_handler(request, http_exc)

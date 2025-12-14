# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE

from logging import Logger, getLogger
from typing import Final

from fastapi import APIRouter

from dcs_pylot_dash.api.api_model import APISourceModel


class APIRoutes:

    SOURCE_MODEL: Final[str] = "/source-model"


class MainRouter:
    LOGGER: Logger = getLogger(__name__)

    @classmethod
    async def create_router(cls) -> APIRouter:
        api_router: APIRouter = APIRouter()

        @api_router.get("/")
        async def hello() -> str:
            return "Hello World!"

        @api_router.get(APIRoutes.SOURCE_MODEL)
        async def get_source_model() -> APISourceModel:
            return APISourceModel()

        cls.LOGGER.info("MainRouter created")
        return api_router

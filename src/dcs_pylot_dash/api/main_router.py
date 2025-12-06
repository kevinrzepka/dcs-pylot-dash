#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE

from logging import Logger, getLogger

from fastapi import APIRouter


class MainRouter:
    LOGGER: Logger = getLogger(__name__)

    @classmethod
    async def create_router(cls) -> APIRouter:
        api_router: APIRouter = APIRouter()

        @api_router.get("/")
        async def hello() -> str:
            return "Hello World!"

        cls.LOGGER.info("MainRouter created")
        return api_router

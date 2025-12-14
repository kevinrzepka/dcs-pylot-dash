# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from logging import Logger
from typing import Final

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from dcs_pylot_dash.api.main_router import MainRouter


class DCSPylotDashAppSettings(BaseSettings):
    app_name: str = "DCSPylotDashAPI"
    app_version: str = "v1.0.0"


class DcsPylotDash:

    LOGGER: Final[Logger] = logging.getLogger(__name__)

    @staticmethod
    async def create_app() -> FastAPI:
        app_settings: DCSPylotDashAppSettings = DCSPylotDashAppSettings()
        fast_api: FastAPI = FastAPI(title=app_settings.app_name, version=app_settings.app_version)
        fast_api.include_router(await MainRouter.create_router(), prefix="/api/v1")
        DcsPylotDash.LOGGER.info(f"mounted routes: {fast_api.routes}")
        return fast_api

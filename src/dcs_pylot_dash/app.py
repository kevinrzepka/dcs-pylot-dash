# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from logging import Logger
from pathlib import Path
from typing import Final

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from dcs_pylot_dash.api.main_router import MainRouter
from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings, DCSPylotDashAppMetaSettings


class DcsPylotDash:

    LOGGER: Final[Logger] = logging.getLogger(__name__)

    @staticmethod
    async def create_app() -> FastAPI:
        env_settings_file_path_str: str | None = None
        meta_settings: DCSPylotDashAppMetaSettings = DCSPylotDashAppMetaSettings()
        if meta_settings.settings_file_path is not None:
            env_settings_file_path: Path = Path(meta_settings.settings_file_path).resolve(strict=True)
            env_settings_file_path_str = str(env_settings_file_path.absolute())
            DcsPylotDash.LOGGER.info(f"Loading settings from: {env_settings_file_path}")

        app_settings: DCSPylotDashAppSettings = DCSPylotDashAppSettings(
            settings_file_path=env_settings_file_path_str, _env_file=env_settings_file_path_str
        )
        DcsPylotDash.LOGGER.info(f"App settings: {app_settings}")

        fast_api: FastAPI = FastAPI(title=app_settings.app_name, version=app_settings.app_version, openapi_url=None)
        fast_api.include_router(await MainRouter.create_router(app_settings), prefix="/api/v1")

        if app_settings.mount_ui:
            DcsPylotDash.LOGGER.info("Mounting static router")
            ui_base_dir: Path = (Path(__file__).parent / Path(app_settings.ui_base_dir)).resolve(strict=True)
            fast_api.mount("/", StaticFiles(directory=ui_base_dir, html=True))
            # fast_api.include_router(await StaticRouter.create_router(app_settings), prefix="")

        DcsPylotDash.LOGGER.info(f"mounted routes: {fast_api.routes}")
        return fast_api

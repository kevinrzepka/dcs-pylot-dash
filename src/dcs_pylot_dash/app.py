# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from logging import Logger
from pathlib import Path
from typing import Final

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse

from dcs_pylot_dash.api.api_routes import APIRoutes
from dcs_pylot_dash.api.main_router import MainRouter
from dcs_pylot_dash.app_exception_handlers import AppExceptionHandlers
from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings, DCSPylotDashAppMetaSettings
from dcs_pylot_dash.exceptions import DCSPylotDashResourceNotFoundException
from dcs_pylot_dash.utils.resource_provider import ResourceProvider
from dcs_pylot_dash.utils.string_utils import StringUtils


class DcsPylotDash:

    API_PATH: Final[str] = "/api/v1"

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
        resource_provider: ResourceProvider = ResourceProvider(app_settings.resources_dir_path)

        fast_api: FastAPI = FastAPI(title=app_settings.app_name, version=app_settings.app_version, openapi_url=None)
        AppExceptionHandlers.add_exception_handlers(fast_api)
        fast_api.include_router(
            await MainRouter.create_router(app_settings, resource_provider), prefix=DcsPylotDash.API_PATH
        )

        @fast_api.get(APIRoutes.ROBOTS_TXT)
        async def get_robots_txt() -> FileResponse:
            return FileResponse(resource_provider.static_dir / "robots.txt")

        @fast_api.get(APIRoutes.SECURITY_TXT)
        async def get_robots_txt() -> FileResponse:
            return FileResponse(resource_provider.static_dir / "security.txt")

        if app_settings.mount_ui:  # FastAPI does not allow mounting a router with an empty prefix and path
            DcsPylotDash.LOGGER.info("Mounting UI")

            ui_base_dir: Path = Path(app_settings.ui_base_dir).resolve(strict=True)
            ui_root_file_path: Path = resource_provider.resolve_path_from_base(
                ui_base_dir, app_settings.ui_index_file_name
            )

            @fast_api.get("/")
            async def ui_root(request: Request) -> FileResponse:
                return FileResponse(ui_root_file_path)

            @fast_api.get("/{full_path:path}")
            async def catch_all(request: Request, full_path: str) -> FileResponse:
                resource_path: Path = resource_provider.resolve_path_from_base(ui_base_dir, full_path)
                if resource_path.exists():
                    DcsPylotDash.LOGGER.info(f"Serving resource: {resource_path.absolute()}")
                    return FileResponse(resource_path)
                elif StringUtils.is_not_empty(resource_path.suffix):
                    raise DCSPylotDashResourceNotFoundException(f"Resource not found: {full_path}")
                else:
                    DcsPylotDash.LOGGER.warning(f"Resource not found: {resource_path.absolute()}, serving UI")
                    return FileResponse(ui_root_file_path)

        DcsPylotDash.LOGGER.info(f"mounted routes: {fast_api.routes}")
        return fast_api

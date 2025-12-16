# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE

from logging import Logger, getLogger
from typing import Final

from fastapi import APIRouter

from dcs_pylot_dash.api.api_model import APISourceModel
from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings
from dcs_pylot_dash.service.app_metadata_service import AppMetadataService, AppMetadata
from dcs_pylot_dash.service.notice_service import NoticesContainer, NoticesService, NoticesSettings
from dcs_pylot_dash.service.source_model_service import SourceModelService
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


class APIRoutes:

    SOURCE_MODEL: Final[str] = "/source-model"
    NOTICES: Final[str] = "/notices"
    METADATA: Final[str] = "/metadata"


class MainRouter:
    LOGGER: Logger = getLogger(__name__)

    @classmethod
    async def create_router(cls, app_settings: DCSPylotDashAppSettings) -> APIRouter:

        resource_provider: ResourceProvider = ResourceProvider()
        source_model_service: SourceModelService = SourceModelService(resource_provider)
        notices_settings: NoticesSettings = NoticesSettings(_env_file=app_settings.settings_file_path)
        notices_service: NoticesService = NoticesService(notices_settings, resource_provider)
        metadata_service: AppMetadataService = AppMetadataService(app_settings)

        api_router: APIRouter = APIRouter()

        @api_router.get(APIRoutes.SOURCE_MODEL)
        async def get_source_model() -> APISourceModel:
            return source_model_service.api_source_model

        @api_router.get(APIRoutes.NOTICES)
        async def get_notices() -> NoticesContainer:
            return notices_service.notices

        @api_router.get(APIRoutes.METADATA)
        async def get_metadata() -> AppMetadata:
            return metadata_service.metadata

        cls.LOGGER.info("MainRouter created")
        return api_router

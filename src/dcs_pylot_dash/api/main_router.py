# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from io import BytesIO
from logging import Logger, getLogger

from fastapi import APIRouter
from starlette.responses import Response

from dcs_pylot_dash.api.api_model import APISourceModel, APIExportModel
from dcs_pylot_dash.api.api_routes import APIRoutes
from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings
from dcs_pylot_dash.exceptions import DCSPylotDashInvalidInputException
from dcs_pylot_dash.service.api_model_export_service import APIModelExportService
from dcs_pylot_dash.service.app_metadata_service import AppMetadataService, AppMetadata
from dcs_pylot_dash.service.notice_service import NoticesContainer, NoticesService, NoticesSettings
from dcs_pylot_dash.service.source_model_service import SourceModelService
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


class MainRouter:
    LOGGER: Logger = getLogger(__name__)

    @classmethod
    async def create_router(
        cls, app_settings: DCSPylotDashAppSettings, resource_provider: ResourceProvider
    ) -> APIRouter:

        source_model_service: SourceModelService = SourceModelService(resource_provider)
        notices_settings: NoticesSettings = NoticesSettings(_env_file=app_settings.settings_file_path)
        notices_service: NoticesService = NoticesService(notices_settings, resource_provider)
        metadata_service: AppMetadataService = AppMetadataService(app_settings)

        api_model_export_service: APIModelExportService = APIModelExportService(
            app_settings, source_model_service, notices_service, resource_provider
        )

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

        @api_router.post(APIRoutes.GENERATE)
        async def generate(api_export_model: APIExportModel) -> Response:
            if api_export_model.is_empty:
                raise DCSPylotDashInvalidInputException("empty export model")

            bytes_io: BytesIO = api_model_export_service.export_model(api_export_model)
            return Response(content=bytes_io.getvalue(), media_type="application/zip")

        cls.LOGGER.info(f"{__name__} created")
        return api_router

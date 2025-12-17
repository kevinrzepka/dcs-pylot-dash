# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from io import BytesIO
from zipfile import PyZipFile

from dcs_pylot_dash.api.api_model import APIExportModel
from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings
from dcs_pylot_dash.exceptions import DCSPylotDashInvalidInputException
from dcs_pylot_dash.service.dcs_model_internal import InternalModelField
from dcs_pylot_dash.service.export_model import ExportModel, ExportModelField, LuaGeneratorOutput
from dcs_pylot_dash.service.html_ui_generator import HtmlUIGenerator, HtmlUiGeneratorSettings, HtmlUIGeneratorOutput
from dcs_pylot_dash.service.lua_generator import LuaGenerator, LuaGeneratorSettings
from dcs_pylot_dash.service.notice_service import NoticesService
from dcs_pylot_dash.service.source_model_service import SourceModelService
from dcs_pylot_dash.service.units import Unit
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


class APIModelExportService:

    _notices_service: NoticesService
    _resource_provider: ResourceProvider
    _app_settings: DCSPylotDashAppSettings
    _source_model_service: SourceModelService

    def __init__(
        self,
        app_settings: DCSPylotDashAppSettings,
        source_model_service: SourceModelService,
        notices_service: NoticesService,
        resource_provider: ResourceProvider,
    ):
        self._resource_provider = resource_provider
        self._app_settings = app_settings
        self._source_model_service = source_model_service
        self._notices_service = notices_service

    def export_model(self, api_model: APIExportModel) -> BytesIO:
        export_model: ExportModel = self._build_export_model(api_model)
        lua_generator: LuaGenerator = LuaGenerator(
            LuaGeneratorSettings(), self._resource_provider, self._notices_service.notices
        )
        lua_generator_output: LuaGeneratorOutput = lua_generator.generate(
            self._source_model_service.internal_model, export_model
        )
        html_generator: HtmlUIGenerator = HtmlUIGenerator(HtmlUiGeneratorSettings(), self._resource_provider)
        html_generator_output: HtmlUIGeneratorOutput = html_generator.generate(export_model)

        in_memory_file: BytesIO = BytesIO()
        with PyZipFile(in_memory_file, "w") as zip_file:
            zip_file.writestr("dcs_pylot_dash.html", html_generator_output.html_content)
            zip_file.writestr(export_model.lua_export_settings.output_script_name, lua_generator_output.script_content)
            zip_file.writestr("add-content-to-Export.lua", lua_generator_output.export_content)
            if first_invalid_zip_file_name := zip_file.testzip() is not None:
                raise DCSPylotDashInvalidInputException(f"zip file is invalid: {first_invalid_zip_file_name}")

        return in_memory_file

    def _build_export_model(self, api_model: APIExportModel) -> ExportModel:
        export_model: ExportModel = ExportModel()
        for i_row, row in enumerate(api_model.rows):
            for i_col, field in enumerate(row.fields):
                internal_field: InternalModelField | None = self._source_model_service.get_field(field.field_id)
                if internal_field is None:
                    raise DCSPylotDashInvalidInputException(f"no such field {field.field_id}")
                output_unit: Unit | None = self._source_model_service.get_unit_for_field(field.field_id, field.unit_id)
                if output_unit is None:
                    raise DCSPylotDashInvalidInputException(f"no such unit {field.unit_id} for field {field.field_id}")

                export_model_field: ExportModelField = ExportModelField(
                    name=internal_field.name,
                    internal_field_name=internal_field.dotted_name,
                    display_name_override=field.display_name,
                    output_unit_override=output_unit,
                    row=i_row,
                    col=i_col,
                    decimal_digits=internal_field.default_decimal_digits,
                )
                export_model.fields.append(export_model_field)

        return export_model

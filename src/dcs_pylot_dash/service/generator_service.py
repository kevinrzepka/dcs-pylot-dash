# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from enum import StrEnum, auto
from io import BytesIO
from logging import Logger
from typing import Final
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


class ReadmeTemplateVar(StrEnum):
    APP_TITLE = auto()
    APP_VERSION = auto()
    OUTPUT_SCRIPT_NAME = auto()
    HTML_FILE_NAME = auto()


class GeneratorService:

    LOGGER: Final[Logger] = logging.getLogger(__name__)

    SAMPLE_MODEL_FILE_NAME: Final[str] = "sample_api_export_model.json"
    README_TEMPLATE_NAME: Final[str] = "readme.template.txt"

    _lua_generator: LuaGenerator
    _html_generator: HtmlUIGenerator
    _notices_service: NoticesService
    _resource_provider: ResourceProvider
    _app_settings: DCSPylotDashAppSettings
    _source_model_service: SourceModelService

    _readme_template: str = ""

    _sample_model: APIExportModel

    def __init__(
        self,
        app_settings: DCSPylotDashAppSettings,
        source_model_service: SourceModelService,
        notices_service: NoticesService,
        resource_provider: ResourceProvider,
    ):
        self._app_settings = app_settings
        self._resource_provider = resource_provider
        self._notices_service = notices_service
        self._source_model_service = source_model_service
        self._lua_generator = LuaGenerator(
            LuaGeneratorSettings(), self._resource_provider, self._notices_service.notices
        )
        self._html_generator = HtmlUIGenerator(
            HtmlUiGeneratorSettings(app_name=app_settings.app_name, app_version=app_settings.app_version),
            self._resource_provider,
            notices_service,
        )
        self._read_readme_template()
        self._load_sample_model()

    def _load_sample_model(self) -> None:
        json_content: str = self._resource_provider.read_sample_model_file(self.SAMPLE_MODEL_FILE_NAME)
        self._sample_model = APIExportModel.model_validate_json(json_content)

    def _read_readme_template(self) -> None:
        self.LOGGER.info(f"Reading readme template: {self.README_TEMPLATE_NAME}")
        readme_template: str = self._resource_provider.read_template_file(self.README_TEMPLATE_NAME)
        readme_template = self._fill_readme(readme_template, ReadmeTemplateVar.APP_TITLE, self._app_settings.app_name)
        readme_template = self._fill_readme(
            readme_template, ReadmeTemplateVar.APP_VERSION, self._app_settings.app_version
        )
        self._readme_template = readme_template

    def export_model(self, api_model: APIExportModel) -> BytesIO:
        self.LOGGER.info("Generating from export model")
        export_model: ExportModel = self._build_export_model(api_model)
        lua_generator_output: LuaGeneratorOutput = self._lua_generator.generate(
            self._source_model_service.internal_model, export_model
        )
        html_generator_output: HtmlUIGeneratorOutput = self._html_generator.generate(export_model)

        html_file_name: str = f"{self._html_generator.app_name}.html"
        output_script_file_name: str = export_model.lua_export_settings.output_script_name
        readme_content: str = self._build_readme(html_file_name, output_script_file_name)

        in_memory_file: BytesIO = BytesIO()
        with PyZipFile(in_memory_file, "w") as zip_file:
            zip_file.writestr(html_file_name, html_generator_output.html_content)
            zip_file.writestr(output_script_file_name, lua_generator_output.script_content)
            zip_file.writestr("add-to-Export.lua", lua_generator_output.export_content)
            zip_file.writestr("license.txt", self._notices_service.notices.license_txt)
            zip_file.writestr("readme.txt", readme_content)
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

    @staticmethod
    def _fill_readme(template: str, template_var: ReadmeTemplateVar, value: str) -> str:
        template_var_string: str = f"%{template_var}%"
        return template.replace(template_var_string, value)

    def _build_readme(self, html_file_name: str, output_script_file_name: str) -> str:
        readme_content: str = self._fill_readme(self._readme_template, ReadmeTemplateVar.HTML_FILE_NAME, html_file_name)
        return self._fill_readme(readme_content, ReadmeTemplateVar.OUTPUT_SCRIPT_NAME, output_script_file_name)

    @property
    def sample_model(self) -> APIExportModel:
        return self._sample_model

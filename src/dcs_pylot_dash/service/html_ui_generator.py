# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from enum import StrEnum, auto
from typing import ClassVar

from pydantic import BaseModel

from dcs_pylot_dash.service.dcs_common_data_types import LoReturnType
from dcs_pylot_dash.service.export_model import ExportModel, Color
from dcs_pylot_dash.service.resource_provider import ResourceProvider

LOGGER = logging.getLogger(__name__)


class HtmlTemplateVar(StrEnum):
    """
    Placeholders in the HTML main template. Some are 'standalone', some in the form: //%foo%
    """

    BIND_ADDRESS = auto()
    BIND_PORT = auto()
    SET_INTERVAL_CALL = auto()
    TITLE_MAP_ENTRIES = auto()
    UNIT_MAP_ENTRIES = auto()
    DECIMAL_DIGITS_MAP_ENTRIES = auto()
    POSITION_MAP_ENTRIES = auto()
    COLOR_SCALE_MAP_ENTRIES = auto()
    COLOR_SCALE_CLASSES_ENTRIES = auto()
    APP_TITLE = auto()
    APP_VERSION = auto()


class HtmlUIGeneratorOutput(BaseModel):
    html_content: str


class HtmlUiGeneratorSettings(BaseModel):
    """
    Settings for the HtmlUIGenerator, regardless of a specific export model
    """

    MAIN_TEMPLATE_NAME_DEFAULT: ClassVar[str] = "template.main.html"
    TEMPLATE_VAR_DELIMITER_DEFAULT: ClassVar[str] = "%"
    SCRIPT_INDENTATION_DEFAULT: ClassVar[int] = 4
    TITLE_MAP_VAR_NAME_DEFAULT: ClassVar[str] = "titleMap"
    UNIT_MAP_VAR_NAME_DEFAULT: ClassVar[str] = "unitMap"
    DECIMAL_DIGITS_MAP_VAR_NAME_DEFAULT: ClassVar[str] = "decimalDigitsMap"
    POSITION_MAP_VAR_NAME_DEFAULT: ClassVar[str] = "positionMap"
    COLOR_SCALE_MAP_VAR_NAME_DEFAULT: ClassVar[str] = "colorScaleMap"
    COLOR_SCALE_CLASSES_VAR_NAME_DEFAULT: ClassVar[str] = "colorScaleClasses"

    main_template_name: str = MAIN_TEMPLATE_NAME_DEFAULT
    template_var_delimiter: str = TEMPLATE_VAR_DELIMITER_DEFAULT
    script_indentation: int = SCRIPT_INDENTATION_DEFAULT
    title_map_var_name: str = TITLE_MAP_VAR_NAME_DEFAULT
    unit_map_var_name: str = UNIT_MAP_VAR_NAME_DEFAULT
    decimal_digits_map_var_name: str = DECIMAL_DIGITS_MAP_VAR_NAME_DEFAULT
    position_map_var_name: str = POSITION_MAP_VAR_NAME_DEFAULT
    color_scale_map_var_name: str = COLOR_SCALE_MAP_VAR_NAME_DEFAULT
    color_scale_classes_var_name: str = COLOR_SCALE_CLASSES_VAR_NAME_DEFAULT


class HtmlUIGenerator:
    """
    Generates an HTML UI for an ExportModel
    """

    _settings: HtmlUiGeneratorSettings
    _resource_provider: ResourceProvider

    def __init__(self, settings: HtmlUiGeneratorSettings, resource_provider: ResourceProvider) -> None:
        self._settings = settings
        self._resource_provider = resource_provider
        self._read_template()

    def _read_template(self) -> None:
        LOGGER.info(f"Reading main template: {self._settings.main_template_name}")
        self._main_template = self._resource_provider.read_template_file(self._settings.main_template_name)

    def _add_line(self, content: str, line: str, *, indent_factor: int = 1) -> str:
        return content + "\n" + (self._settings.script_indentation * indent_factor) * " " + line

    def _create_title_map_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.title_map_var_name
        content: str = ""
        for field in export_model.fields:
            content = self._add_line(content, f"{var_name}.set('data.{field.name}', '{field.effective_display_name}');")
        return content

    def _create_unit_map_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.unit_map_var_name
        content: str = ""
        for field in export_model.fields:
            content = self._add_line(content, f"{var_name}.set('data.{field.name}', '{field.unit_label}');")
        return content

    def _create_decimal_digits_map_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.decimal_digits_map_var_name
        content: str = ""
        for field in export_model.fields:
            if field.internal_field.return_type == LoReturnType.NUMBER:
                line: str = f"{var_name}.set('data.{field.name}', '{field.decimal_digits}');"
                content = self._add_line(content, line)
        return content

    def _create_position_map_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.position_map_var_name
        content: str = ""
        for field in export_model.fields:
            if field.has_position:
                map_value: str = f"[{field.row}, {field.col}]"
                content = self._add_line(content, f"{var_name}.set('data.{field.name}', {map_value});")
        return content

    def _create_color_scale_map_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.color_scale_map_var_name
        content: str = ""
        for field in export_model.fields:
            if field.has_color_scale:
                content = self._add_line(content, f"{var_name}.set('data.{field.name}', []);")
                for c in field.color_scale:
                    min_value = c.min if c.min is not None else "null"
                    max_value = c.max if c.max is not None else "null"
                    list_entry: str = f"{{min: {min_value}, max: {max_value}, color: '{c.color}'}}"
                    content = self._add_line(content, f"{var_name}.get('data.{field.name}').push({list_entry});")
        return content

    def create_color_scale_classes_entries(self, export_model: ExportModel) -> str:
        var_name: str = self._settings.color_scale_classes_var_name
        content: str = ""
        for c in Color:
            content = self._add_line(content, f"{var_name}.push('text-{c}');")
        return content

    def generate(self, export_model: ExportModel) -> HtmlUIGeneratorOutput:
        title_map_entries: str = self._create_title_map_entries(export_model)
        unit_map_entries: str = self._create_unit_map_entries(export_model)
        decimal_digits_map_entries: str = self._create_decimal_digits_map_entries(export_model)
        position_map_entries: str = self._create_position_map_entries(export_model)
        color_scale_map_entries: str = self._create_color_scale_map_entries(export_model)
        color_scale_classes_entries: str = self.create_color_scale_classes_entries(export_model)

        html: str = self._main_template
        http_settings = export_model.http_server_settings
        html = self._fill(html, HtmlTemplateVar.APP_TITLE, "TODO")
        html = self._fill(html, HtmlTemplateVar.APP_VERSION, "TODO")
        html = self._fill(html, HtmlTemplateVar.BIND_ADDRESS, http_settings.bind_address)
        html = self._fill(html, HtmlTemplateVar.BIND_PORT, str(http_settings.bind_port))
        html = self._fill(html, HtmlTemplateVar.TITLE_MAP_ENTRIES, title_map_entries, comment=True)
        html = self._fill(html, HtmlTemplateVar.UNIT_MAP_ENTRIES, unit_map_entries, comment=True)
        html = self._fill(html, HtmlTemplateVar.DECIMAL_DIGITS_MAP_ENTRIES, decimal_digits_map_entries, comment=True)
        html = self._fill(html, HtmlTemplateVar.POSITION_MAP_ENTRIES, position_map_entries, comment=True)
        html = self._fill(html, HtmlTemplateVar.COLOR_SCALE_MAP_ENTRIES, color_scale_map_entries, comment=True)
        html = self._fill(html, HtmlTemplateVar.COLOR_SCALE_CLASSES_ENTRIES, color_scale_classes_entries, comment=True)

        html = self._fill(
            html,
            HtmlTemplateVar.SET_INTERVAL_CALL,
            f"setInterval(updateData, {export_model.ui_export_settings.fetch_data_interval_ms})",
            comment=True,
        )

        return HtmlUIGeneratorOutput(html_content=html)

    def _fill(self, template: str, template_var: HtmlTemplateVar, value: str, *, comment: bool = False) -> str:
        delimiter = self._settings.template_var_delimiter
        template_var_string: str = f"{delimiter}{template_var}{delimiter}"
        if comment:
            template_var_string: str = "//" + template_var_string
        return template.replace(template_var_string, value)

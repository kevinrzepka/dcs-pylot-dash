# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from enum import StrEnum, auto
from typing import ClassVar, Any

from pydantic import BaseModel

from dcs_pylot_dash.service.dcs_common_data_types import LoReturnType
from dcs_pylot_dash.service.dcs_model_internal import InternalModel, InternalModelField
from dcs_pylot_dash.service.export_model import (
    LuaGeneratorOutput,
    ExportModel,
    ExportModelField,
    LuaExportSettings,
    ExportModelTreeNode,
    HttpServerSettings,
)
from dcs_pylot_dash.service.notice_service import NoticesContainer
from dcs_pylot_dash.service.units import UnitConverter, UnitFormatters
from dcs_pylot_dash.utils.resource_provider import ResourceProvider

LOGGER = logging.getLogger(__name__)


class LuaTemplateVar(StrEnum):
    OUTPUT_SCRIPT_NAME = auto()
    DATA_CONTENT = auto()
    SOCKET_TIMEOUT = auto()
    BIND_ADDRESS = auto()
    BIND_PORT = auto()
    MAX_CONNECTIONS = auto()
    LOG_PREFIX = auto()
    COPYRIGHT = auto()


class LuaGeneratorSettings(BaseModel):
    """
    Internal settings for the LuaGenerator
    """

    MAIN_TEMPLATE_NAME_DEFAULT: ClassVar[str] = "main.lua.template"
    EXPORT_TEMPLATE_NAME_DEFAULT: ClassVar[str] = "export.lua.template"
    TEMPLATE_VAR_DELIMITER_DEFAULT: ClassVar[str] = "%"

    main_template_name: str = MAIN_TEMPLATE_NAME_DEFAULT
    export_template_name: str = EXPORT_TEMPLATE_NAME_DEFAULT
    template_var_delimiter: str = TEMPLATE_VAR_DELIMITER_DEFAULT


class LuaGenerator:
    _settings: LuaGeneratorSettings
    _resource_provider: ResourceProvider
    _notices_container: NoticesContainer
    _main_template: str
    _export_template: str

    _data_var: ClassVar[str] = "data"

    _default_lo_return_values: dict[LoReturnType, str] = {
        LoReturnType.TABLE: "{}",
        LoReturnType.STRING: '""',
        LoReturnType.NUMBER: "0",
        LoReturnType.BOOLEAN: "false",
        LoReturnType.LIST: "{}",
    }

    def __init__(
        self, settings: LuaGeneratorSettings, resource_provider: ResourceProvider, notices_container: NoticesContainer
    ) -> None:
        self._settings = settings
        self._resource_provider = resource_provider
        self._notices_container = notices_container
        self._read_templates()

    def _read_templates(self) -> None:
        LOGGER.info(f"Reading main template: {self._settings.main_template_name}")
        main_template: str = self._resource_provider.read_template_file(self._settings.main_template_name)
        self._main_template = self._fill(main_template, LuaTemplateVar.COPYRIGHT, self._notices_container.license_txt)
        LOGGER.info(f"Reading export template: {self._settings.main_template_name}")
        self._export_template = self._resource_provider.read_template_file(self._settings.export_template_name)

    def _fill(self, template: str, template_var: LuaTemplateVar, value: str) -> str:
        delimiter = self._settings.template_var_delimiter
        template_var_string: str = f"{delimiter}{template_var}{delimiter}"
        return template.replace(template_var_string, value)

    @staticmethod
    def _build_export_tree(export_model: ExportModel) -> ExportModelTreeNode:
        root: ExportModelTreeNode = ExportModelTreeNode(name="")
        for field in export_model.fields:
            root.add_node(field)
        return root

    @staticmethod
    def _add_line(content: str, line: str, settings: LuaExportSettings, *, indent_factor: int = 1) -> str:
        contents_start: str = content
        if len(content) > 0:
            contents_start += "\n" + (settings.script_indentation * indent_factor) * " "
        return contents_start + line

    def _add_sc_root_fields(self, export_model: ExportModel, sc: str) -> str:
        for root_field in export_model.internal_root_fields.values():
            default_value: str = self._default_lo_return_values[root_field.return_type]
            sc = self._add_line(
                sc,
                f"local {root_field.name} = safe_get({root_field.lo_function}, {default_value})",
                export_model.lua_export_settings,
            )
        return sc

    def _add_sc_node(self, node: ExportModelTreeNode, sc: str, settings: LuaExportSettings) -> str:
        if node.has_export_field:  # then all necessary objects must have been created before
            internal_field: InternalModelField = node.export_field.internal_field
            if internal_field.has_list_field_in_hierarchy:  # list fields cannot be leaves
                list_field: InternalModelField = internal_field.next_list_field_in_hierarchy
                sc = self._add_line(sc, f"for i, v in ipairs({list_field.dotted_name}) do", settings)
                node_at_index: str = f"{self._data_var}.{node.parent.name}"
                sc = self._add_line(sc, f"{node_at_index}[i] = {{}}", settings, indent_factor=2)
                var_name: str = f"{node_at_index}[i].{node.local_name}"
                var_value: str = f"{internal_field.parent.dotted_name}[i].{internal_field.name}"
                sc = self._add_line(sc, f"{var_name} = {var_value}", settings, indent_factor=2)
                sc = self._add_line(sc, "end", settings)
            else:
                line: str = f"{self._data_var}.{node.name} = "
                if UnitFormatters.has_formatter(node.export_field.effective_unit):
                    formatter_function: str | None = UnitFormatters.get_formatter(node.export_field.effective_unit)
                    line += f"{formatter_function}({internal_field.dotted_name})"
                else:
                    line = f"{self._data_var}.{node.name} = "
                    if internal_field.return_type == LoReturnType.NUMBER:
                        line += f"({internal_field.dotted_name} or 0)"
                    else:
                        line += f"{internal_field.dotted_name}"

                    if internal_field.abs_base_value is not None:
                        line += f" * {internal_field.abs_base_value}"
                    if node.export_field.output_unit_override is not None:
                        factor: float | None = UnitConverter.get_conversion_factor(
                            internal_field.unit, node.export_field.output_unit_override
                        )
                        if factor is not None and factor != 1.0:
                            line += f" * {factor}"
                sc = self._add_line(sc, line, settings)
        else:
            sc = self._add_line(sc, f"{self._data_var}.{node.name} = {{}}", settings)
            for child_node in node.nodes.values():
                sc = self._add_sc_node(child_node, sc, settings)
        return sc

    def _add_sc_data(self, export_model: ExportModel, sc: str) -> str:
        tree: ExportModelTreeNode = self._build_export_tree(export_model)
        for node in tree.nodes.values():
            sc = self._add_sc_node(node, sc, export_model.lua_export_settings)
        return sc

    def _build_script_content(self, export_model: ExportModel) -> str:
        sc: str = ""
        sc = self._add_sc_root_fields(export_model, sc)
        sc = self._add_sc_data(export_model, sc)
        return sc

    @staticmethod
    def _resolve_field(internal_model: InternalModel, export_model_field: ExportModelField) -> InternalModelField:
        internal_field: InternalModelField | None = internal_model.get_field(export_model_field.internal_field_name)
        if internal_field is None:
            LOGGER.warning(f"Field {export_model_field.internal_field_name} not found in model")
        else:
            export_model_field.internal_field = internal_field
        return internal_field

    def generate(self, internal_model: InternalModel, export_model: ExportModel) -> LuaGeneratorOutput:
        """
        General approach:
        - resolve all fields
        - get all root fields
        - for each root field: Call function, attach the result to exported data
        - for each field: apply the unit conversion factor (and abs factors) to exported data
        :param internal_model:
        :param export_model:
        :return: LuaGeneratorOutput
        """
        for f in export_model.fields:
            self._resolve_field(internal_model, f)

        quoted_log_prefix: str = f'"{export_model.lua_export_settings.log_prefix}"'

        export_content: str = self._fill(
            self._export_template,
            LuaTemplateVar.OUTPUT_SCRIPT_NAME,
            export_model.lua_export_settings.output_script_name,
        )
        export_content = self._fill(export_content, LuaTemplateVar.COPYRIGHT, self._notices_container.license_txt)
        export_content = self._fill(export_content, LuaTemplateVar.LOG_PREFIX, quoted_log_prefix)

        sc: str = self._fill(self._main_template, LuaTemplateVar.DATA_CONTENT, self._build_script_content(export_model))

        def _fill_sc(sc_: str, template_var: LuaTemplateVar, value: Any) -> str:
            return self._fill(sc_, template_var, str(value))

        sc = _fill_sc(sc, LuaTemplateVar.LOG_PREFIX, quoted_log_prefix)
        http_settings: HttpServerSettings = export_model.http_server_settings
        sc = _fill_sc(sc, LuaTemplateVar.SOCKET_TIMEOUT, http_settings.socket_timeout)
        sc = _fill_sc(sc, LuaTemplateVar.BIND_ADDRESS, f'"{http_settings.bind_address}"')
        sc = _fill_sc(sc, LuaTemplateVar.BIND_PORT, http_settings.bind_port)
        sc = _fill_sc(sc, LuaTemplateVar.MAX_CONNECTIONS, http_settings.max_connections)

        return LuaGeneratorOutput(
            export_content=export_content,
            script_content=sc,
        )

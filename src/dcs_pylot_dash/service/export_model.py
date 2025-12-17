# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from enum import StrEnum, auto
from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel, model_validator

from dcs_pylot_dash.exceptions import DCSPylotDashInvalidInputException
from dcs_pylot_dash.service.dcs_model_internal import InternalModelField
from dcs_pylot_dash.service.units import Unit, UnitLabels
from dcs_pylot_dash.utils.string_utils import StringUtils

LOGGER = logging.getLogger(__name__)


class InvalidExportModelError(DCSPylotDashInvalidInputException):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Invalid export model: {msg}")


class HttpServerSettings(BaseModel):
    """
    See also: UiModelSettings
    """

    BIND_ADDRESS_LOCALHOST: ClassVar[str] = "127.0.0.1"
    BIND_PORT_DEFAULT: ClassVar[int] = 52025
    MAX_CONNECTIONS_DEFAULT: ClassVar[int] = 5
    SOCKET_TIMEOUT_DEFAULT: ClassVar[int] = 0

    bind_address: str = BIND_ADDRESS_LOCALHOST
    # ephemeral range: 49152 to 65535
    bind_port: int = BIND_PORT_DEFAULT
    max_connections: int = MAX_CONNECTIONS_DEFAULT
    socket_timeout: int = SOCKET_TIMEOUT_DEFAULT


class LuaExportSettings(BaseModel):
    """
    Settings for each generator pass
    """

    EXPORT_SCRIPT_NAME: ClassVar[str] = "Export.lua"
    LOG_PREFIX_DEFAULT: ClassVar[str] = "PyDCSExport"
    SCRIPT_INDENTATION_DEFAULT: ClassVar[int] = 4
    OUTPUT_DIR_DEFAULT: ClassVar[str] = "."
    OUTPUT_SCRIPT_NAME_DEFAULT: ClassVar[str] = "PyDcsExport.lua"

    log_prefix: str = LOG_PREFIX_DEFAULT
    output_dir: str = OUTPUT_DIR_DEFAULT
    output_script_name: str = OUTPUT_SCRIPT_NAME_DEFAULT
    script_indentation: int = SCRIPT_INDENTATION_DEFAULT

    @property
    def output_dir_path(self) -> Path:
        return Path(self.output_dir).resolve()

    @property
    def main_script_output_path(self) -> Path:
        return self.output_dir_path / self.output_script_name

    @property
    def export_script_output_path(self) -> Path:
        return self.output_dir_path / self.EXPORT_SCRIPT_NAME


class Color(StrEnum):
    DANGER = auto()
    WARNING = auto()
    SUCCESS = auto()
    INFO = auto()
    PRIMARY = auto()


class ColorScaleEntry(BaseModel):
    min: int | None = None
    max: int | None = None
    color: Color

    @model_validator(mode="after")
    def validate_color(self) -> Self:
        if self.min is None and self.max is None:
            raise InvalidExportModelError("Invalid colorscale entry: min and max are both None")
        if self.min is not None and self.max is not None and self.min >= self.max:
            raise InvalidExportModelError(f"Invalid colorscale entry: min={self.min} > max={self.max}")
        return self


class ExportModelField(BaseModel):
    DECIMAL_DIGITS_DEFAULT: ClassVar[int] = 0
    FIELD_NAME_NOT_RESOLVED_PREFIX: ClassVar[str] = "NOT_RESOLVED"
    # External name, under which this field will be stored in the JSON response.
    # If dotted, (recursively) creates an object.
    name: str
    # Desired output unit. May or may not be achievable by conversion from the internal unit
    output_unit_override: Unit | None = None
    # If set, overrides the name from InternalModelField.effective_display_name
    display_name_override: str | None = None
    # InternalModelField.dotted_name, used for lookup in InternalModel
    internal_field_name: str
    internal_field: InternalModelField | None = None
    decimal_digits: int = DECIMAL_DIGITS_DEFAULT
    row: int | None = None
    col: int | None = None
    color_scale: list[ColorScaleEntry] = []

    @property
    def internal_list_field_ref(self) -> InternalModelField | None:
        if self.internal_field is None:
            return None
        if self.internal_field.is_list_field:
            return self.internal_field
        return self.internal_field.next_list_field_in_hierarchy

    @property
    def references_list_field(self) -> bool:
        return self.internal_list_field_ref is not None

    @property
    def is_resolved(self) -> bool:
        return self.internal_field is not None

    @property
    def has_position(self) -> bool:
        return self.row is not None and self.col is not None

    @property
    def effective_display_name(self) -> str:
        if self.internal_field is not None:
            return StringUtils.first_non_empty(self.display_name_override, self.internal_field.effective_display_name)
        return f"{self.FIELD_NAME_NOT_RESOLVED_PREFIX}: {self.internal_field_name}"

    @property
    def has_color_scale(self) -> bool:
        return len(self.color_scale) > 0

    @property
    def name_chunks(self) -> list[str]:
        return self.name.split(".")

    @property
    def unit_label(self) -> str:
        unit: Unit = self.output_unit_override
        if unit is None:
            unit = self.internal_field.unit
        return UnitLabels.default.get(unit) or ""


class UiExportSettings(BaseModel):
    """
    See also: HttpServerSettings
    """

    FETCH_DATA_INTERVAL_MS_DEFAULT: ClassVar[int] = 200

    fetch_data_interval_ms: int = FETCH_DATA_INTERVAL_MS_DEFAULT


class ExportModel(BaseModel):
    """
    Described the output structure returned to the user.
    """

    # Cannot use a dict with key: InternalModelField.dotted_name, because the same data might be shown
    # multiple times w/ different units, e.g., fuel in lbs and kg, TAS in kts and m/s
    fields: list[ExportModelField] = []
    lua_export_settings: LuaExportSettings = LuaExportSettings()
    ui_export_settings: UiExportSettings = UiExportSettings()
    http_server_settings: HttpServerSettings = HttpServerSettings()

    @property
    def internal_root_fields(self) -> dict[str, InternalModelField]:
        return {
            intf.name: intf for intf in (extf.internal_field.root_field for extf in self.fields if extf.is_resolved)
        }


class ExportModelTreeNode(BaseModel):
    """
    Used to create the output structure, which may be different from the obtained lua structure.
    """

    # Dotted name from the root. The parent of this node will only have the last chunk as key in nodes
    name: str
    # Key: Single chunk (of dotted name), i.e., a "local" name
    nodes: dict[str, Self] = {}
    # Only None for root
    parent: Self | None = None
    export_field: ExportModelField | None = None

    @property
    def local_name(self) -> str:
        return self.name.split(".")[-1]

    def get_node(self, name: str) -> Self | None:
        name_chunks: list[str] = name.split(".")
        node: Self | None = self.nodes.get(name_chunks[0])
        if node is None:
            LOGGER.debug(f"Node {name} not found")
            return None
        if len(name_chunks) > 1:
            return node.get_node(".".join(name_chunks[1:]))
        return node

    def add_node(self, export_field: ExportModelField, name_override: str | None = None) -> Self:
        """
        Assumption: Mixing leaf and non-leaf nodes is not allowed.

        :param export_field:
        :param name_override: Should be None when called on the root node.
        :return: Self
        """
        if self.has_export_field:
            raise InvalidExportModelError(
                f"Cannot add node {export_field.name} to {self.name} because it already has an export field"
            )

        if name_override is not None and StringUtils.is_empty(name_override):
            raise InvalidExportModelError(f"Invalid name override: {name_override}")
        node_name: str = name_override or export_field.name
        name_chunks: list[str] = node_name.split(".")
        local_name: str = name_chunks[0]
        node: Self | None = self.get_node(local_name)
        if node is None:
            new_node_name: str = local_name
            if self.parent is not None:
                new_node_name = f"{self.name}.{local_name}"
            node = ExportModelTreeNode(name=new_node_name, parent=self)
            self.nodes[local_name] = node

        if len(name_chunks) == 1:
            node.export_field = export_field
        else:
            node.add_node(export_field, ".".join(name_chunks[1:]))

    @property
    def has_export_field(self) -> bool:
        return self.export_field is not None


class LuaGeneratorOutput(BaseModel):
    # Content to be appended to "~\Saved Games\DCS\Scripts\Export.lua". A single `pcall` line
    export_content: str
    # Content of LuaGeneratorSettings.output_script_name
    script_content: str

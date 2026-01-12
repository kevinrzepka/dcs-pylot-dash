# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import re
from re import Pattern
from typing import ClassVar, Annotated

from pydantic import BaseModel, Field

from dcs_pylot_dash.service.export_model import HttpServerSettings, UiExportSettings
from dcs_pylot_dash.service.units import Unit


class APIUnit(BaseModel):
    display_name: str
    unit_id: str
    symbol: str


class APISourceField(BaseModel):
    display_name: str
    field_id: str
    default_unit_id: str
    available_unit_ids: list[str] = []


class APISourceModel(BaseModel):
    units: list[APIUnit] = []
    fields: list[APISourceField] = []


class APIExportField(BaseModel):
    MAX_FIELD_VALUE_LENGTH: ClassVar[int] = 50
    DISPLAY_NAME_PATTERN: ClassVar[Pattern] = re.compile(r"^[\w\s.()]+$")
    FIELD_ID_PATTERN: ClassVar[Pattern] = re.compile(r"^[\w.]+$")

    display_name: str = Field(max_length=MAX_FIELD_VALUE_LENGTH, pattern=DISPLAY_NAME_PATTERN)
    field_id: str = Field(max_length=MAX_FIELD_VALUE_LENGTH, pattern=FIELD_ID_PATTERN)
    unit_id: Unit


class APIExportRow(BaseModel):
    MAX_FIELDS_PER_ROW: ClassVar[int] = 10

    fields: list[APIExportField] = Field(default_factory=list, max_length=MAX_FIELDS_PER_ROW)

    @property
    def is_empty(self) -> bool:
        return len(self.fields) == 0


class APIExportModelAdvancedSettings(BaseModel):
    lua_bind_address: str | None = None
    lua_bind_port: (
        Annotated[
            int, Field(ge=HttpServerSettings.EPHEMERAL_PORT_RANGE_START, le=HttpServerSettings.EPHEMERAL_PORT_RANGE_END)
        ]
        | None
    ) = None
    poll_interval_ms: (
        Annotated[
            int, Field(ge=UiExportSettings.FETCH_DATA_INTERVAL_MS_MIN, le=UiExportSettings.FETCH_DATA_INTERVAL_MS_MAX)
        ]
        | None
    ) = None


class APIExportModel(BaseModel):
    MAX_ROWS: ClassVar[int] = 10

    rows: list[APIExportRow] = Field(default_factory=list, max_length=MAX_ROWS)
    advanced_settings: APIExportModelAdvancedSettings | None = None

    @property
    def is_empty(self) -> bool:
        if len(self.rows) != 0:
            return all(r.is_empty for r in self.rows)
        return True

# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pydantic import BaseModel


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

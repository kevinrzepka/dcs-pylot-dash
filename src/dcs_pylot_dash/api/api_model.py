# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pydantic import BaseModel, Field


class APIUnit(BaseModel):
    display_name: str
    unit_id: str = Field(alias="unitId")
    symbol: str


class APISourceField(BaseModel):
    display_name: str
    field_id: str = Field(alias="fieldId")


class APISourceModel(BaseModel):
    units: list[APIUnit] = []
    fields: list[APISourceField] = []

# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from typing import Self

from pydantic import BaseModel, model_validator

from dcs_pylot_dash.service.dcs_common_data_types import LoReturnType
from dcs_pylot_dash.service.units import Unit


class ExternalModelError(Exception):

    def __init__(self, msg: str) -> None:
        super().__init__(f"Invalid model: {msg}")


class ExternalModelField(BaseModel):
    """
    Describes the lua structure returned by DCS.
    """

    lo_return_type: LoReturnType
    # only set for top-level fields
    lo_function: str | None = None
    unit: Unit = Unit.NONE
    is_portion: bool = False
    # only set if is_portion
    abs_base_value: float | None = None
    fields: dict[str, Self] = {}
    prototype_ref: str | None = None
    # Optional human-readable name
    display_name: str | None = None

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.unit != Unit.NONE and self.lo_return_type != LoReturnType.NUMBER:
            raise ExternalModelError(f"unit may only be set for return_type {LoReturnType.NUMBER}")

        if self.lo_return_type == LoReturnType.LIST and self.prototype_ref is None:
            raise ExternalModelError(f"prototype_ref must be set for return_type {LoReturnType.LIST}")

        if self.abs_base_value is not None and not self.is_portion:
            raise ExternalModelError(f"abs_base_value may only be set if is_portion")

        if self.is_portion and self.lo_return_type != LoReturnType.NUMBER:
            raise ExternalModelError(f"is_portion may only be set for return_type {LoReturnType.NUMBER}")

        if self.is_portion and self.abs_base_value is None:
            raise ExternalModelError(f"abs_base_value must be set when is_portion")

        if self.prototype_ref is not None:
            if len(self.fields) > 0:
                raise ExternalModelError("fields may not be set when prototype_ref is set")
            if self.lo_return_type not in (None, LoReturnType.LIST):
                raise ExternalModelError(
                    f"when prototype_ref is specified, the only allowed return_type is {LoReturnType.LIST}"
                )

        return self

    @property
    def references_prototype(self) -> bool:
        return self.prototype_ref is not None

    @property
    def is_list_field(self) -> bool:
        return self.lo_return_type == LoReturnType.LIST


class ExternalModel(BaseModel):
    """
    Parsed directly from user input JSON.
    """

    field_prototypes: dict[str, ExternalModelField] = {}
    fields: dict[str, ExternalModelField] = {}

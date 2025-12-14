# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from typing import Final

from dcs_pylot_dash.api.api_model import APISourceModel, APIUnit, APISourceField
from dcs_pylot_dash.service.dcs_model_external import ExternalModel
from dcs_pylot_dash.service.dcs_model_internal import InternalModel
from dcs_pylot_dash.service.units import Unit, UnitConverter, UnitDisplayNames, UnitLabels
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


class SourceModelService:

    EXTERNAL_MODEL_NAME_DEFAULT: Final[str] = "external_model_default.json"

    _resource_provider: ResourceProvider
    _external_model: ExternalModel
    _internal_model: InternalModel
    _api_source_model: APISourceModel

    def __init__(self, resource_provider: ResourceProvider):
        self._resource_provider = resource_provider
        self._load_models()

    def _load_models(self) -> None:
        external_model_src: str = self._resource_provider.read_external_model_file(self.EXTERNAL_MODEL_NAME_DEFAULT)
        external_model: ExternalModel = ExternalModel.model_validate_json(external_model_src)
        self._external_model = external_model
        internal_model: InternalModel = InternalModel(external_model)
        internal_model.populate()
        self._internal_model = internal_model
        self._api_source_model = self._build_api_source_model(internal_model)

    @staticmethod
    def _build_api_source_model(internal_model: InternalModel) -> APISourceModel:
        api_units: list[APIUnit] = []
        api_fields: list[APISourceField] = []

        for unit in Unit:
            unit_display_name: str = UnitDisplayNames.default.get(unit, unit)
            unit_symbol: str = UnitLabels.default.get(unit, "")
            api_unit: APIUnit = APIUnit(unit_id=unit, display_name=unit_display_name, symbol=unit_symbol)
            api_units.append(api_unit)

        for field in internal_model.leaf_fields:
            api_field: APISourceField = APISourceField(
                display_name=field.effective_display_name,
                field_id=field.dotted_name,
                default_unit_id=field.unit,
                available_unit_ids=UnitConverter.get_convertable_units(field.unit),
            )
            api_fields.append(api_field)

        return APISourceModel(units=api_units, fields=api_fields)

    @property
    def api_source_model(self) -> APISourceModel:
        return self._api_source_model

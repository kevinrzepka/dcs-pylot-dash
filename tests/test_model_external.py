# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path

from dcs_pylot_dash.service.dcs_common_data_types import LoReturnType
from dcs_pylot_dash.service.dcs_model_external import ExternalModel


def test_enums():
    assert LoReturnType("table") == LoReturnType.TABLE


def test_parse_model():
    src_json_path: Path = Path(__file__).parent / "data" / "external_model_1.json"
    src_json: str = src_json_path.read_text()
    export_model: ExternalModel = ExternalModel.model_validate_json(src_json)
    assert export_model

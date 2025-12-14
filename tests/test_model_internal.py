# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path

import pytest

from dcs_pylot_dash.service.dcs_model_external import ExternalModel
from dcs_pylot_dash.service.dcs_model_internal import InternalModel


@pytest.fixture
def model_external():
    src_json_path: Path = Path(__file__).parent / "data" / "external_model_1.json"
    src_json: str = src_json_path.read_text()
    external_model: ExternalModel = ExternalModel.model_validate_json(src_json)
    return external_model or None


def test_model_internal(model_external):
    internal_model = InternalModel(model_external)
    internal_model.populate()
    assert internal_model

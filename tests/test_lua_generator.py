# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path

import pytest

from dcs_pylot_dash.service.dcs_model_external import ExternalModel
from dcs_pylot_dash.service.dcs_model_internal import InternalModel
from dcs_pylot_dash.service.export_model import ExportModel, LuaGeneratorOutput
from dcs_pylot_dash.service.lua_generator import LuaGenerator, LuaGeneratorSettings
from dcs_pylot_dash.service.resource_provider import ResourceProvider


@pytest.fixture
def model_external() -> ExternalModel:
    src_json_path: Path = Path(__file__).parent / "data" / "external_model_1.json"
    src_json: str = src_json_path.read_text()
    external_model: ExternalModel = ExternalModel.model_validate_json(src_json)
    return external_model


@pytest.fixture
def export_model() -> ExportModel:
    src_json_path: Path = Path(__file__).parent / "data" / "export_model_3.json"
    src_json: str = src_json_path.read_text()
    return ExportModel.model_validate_json(src_json)


def test_generate(model_external: ExternalModel, export_model: ExportModel):
    internal_model = InternalModel(model_external)
    internal_model.populate()
    assert internal_model
    resource_provider: ResourceProvider = ResourceProvider()
    generator: LuaGenerator = LuaGenerator(LuaGeneratorSettings(), resource_provider)
    generator_output: LuaGeneratorOutput = generator.generate(internal_model, export_model)
    assert generator_output

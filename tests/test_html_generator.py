# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path

import pytest

from dcs_pylot_dash.service.dcs_model_external import ExternalModel
from dcs_pylot_dash.service.dcs_model_internal import InternalModel
from dcs_pylot_dash.service.export_model import ExportModel
from dcs_pylot_dash.service.html_ui_generator import HtmlUIGenerator, HtmlUiGeneratorSettings, HtmlUIGeneratorOutput
from dcs_pylot_dash.service.lua_generator import LuaGenerator, LuaGeneratorSettings
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


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

    output_dir: Path = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    html_output_file_path: Path = output_dir / "main.html"

    internal_model = InternalModel(model_external)
    internal_model.populate()
    assert internal_model
    resource_provider: ResourceProvider = ResourceProvider()
    lua_generator: LuaGenerator = LuaGenerator(LuaGeneratorSettings(), resource_provider)
    lua_generator_output = lua_generator.generate(internal_model, export_model)

    lua_script_output_file_path: Path = output_dir / export_model.lua_export_settings.output_script_name
    export_output_file_path: Path = output_dir / "Export.lua"

    html_generator: HtmlUIGenerator = HtmlUIGenerator(HtmlUiGeneratorSettings(), resource_provider)
    html_generator_output: HtmlUIGeneratorOutput = html_generator.generate(export_model)
    assert html_generator_output

    html_output_file_path.write_text(html_generator_output.html_content, encoding="utf-8")
    lua_script_output_file_path.write_text(lua_generator_output.script_content, encoding="utf-8")
    export_output_file_path.write_text(lua_generator_output.export_content, encoding="utf-8")

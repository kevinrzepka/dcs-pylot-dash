#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import logging.config
from pathlib import Path
from typing import Final

import pytest
import yaml

from copyright_header.main import CopyrightHeaderGenerator, CopyrightHeaderGeneratorSettings

logging_config_path: Path = Path(__file__).parent.parent / "logging.yaml"
with logging_config_path.open() as f:
    logging.config.dictConfig(yaml.safe_load(f))
    logging.getLogger(__name__).info("logging configured")

CASES_DIR: Final[Path] = Path(__file__).parent / "resources" / "cases"


@pytest.fixture
def generator() -> CopyrightHeaderGenerator:
    generator_settings: CopyrightHeaderGeneratorSettings = CopyrightHeaderGeneratorSettings(
        contents_dir_path=Path(__file__).parent / "resources" / "extensions", update_existing=True
    )
    return CopyrightHeaderGenerator(generator_settings)


def case_names() -> list[str]:
    return [d.name for d in CASES_DIR.iterdir()]


@pytest.mark.parametrize("case_name", case_names())
def test_case(generator: CopyrightHeaderGenerator, case_name: str) -> None:
    case_dir: Path = CASES_DIR / case_name
    input_file_path: Path | None = None
    expected_output_file_path: Path | None = None
    for f in case_dir.iterdir():
        if f.stem == "input":
            input_file_path = f
        elif f.stem == "expected":
            expected_output_file_path = f
    if input_file_path is None:
        pytest.fail(f"No input file found in {case_dir}")
    if expected_output_file_path is None:
        pytest.fail(f"No expected output file found in {case_dir}")

    updated_file_content: str | None = generator.update_file_content(input_file_path)
    expected_file_content = expected_output_file_path.read_text()
    assert updated_file_content == expected_file_content

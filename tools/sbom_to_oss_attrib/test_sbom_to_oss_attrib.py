# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging.config
import os
from pathlib import Path

import pytest
import yaml

from sbom_to_oss_attrib.attribution_generator import OssAttributionGenerator
from sbom_to_oss_attrib.attribution_output import AttributionTextFileBuilder

logging_config_path: Path = Path(__file__).parent / "logging.yaml"
with logging_config_path.open() as f:
    logging.config.dictConfig(yaml.safe_load(f))
    logging.getLogger(__name__).info("logging configured")


@pytest.fixture
def sbom_path() -> Path:
    return Path(__file__).parent.parent.parent / "sboms" / "sbom.json"


@pytest.mark.asyncio
async def test_build(sbom_path: Path):
    license_api_token: str = os.getenv("LICENSE_API_TOKEN")
    sbom = OssAttributionGenerator().parse_sbom(sbom_path)
    attribution = await OssAttributionGenerator(github_api_token=license_api_token).build_attribution(sbom_path)
    AttributionTextFileBuilder().output_to_file(attribution, Path("third_party_licenses.txt"))
    assert attribution

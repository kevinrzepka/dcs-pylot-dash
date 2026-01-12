# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import os
from pathlib import Path

import pytest
from fastapi import FastAPI

from dcs_pylot_dash.app import DcsPylotDash


@pytest.mark.asyncio
async def test_app():
    repo_path: Path = Path(__file__).parent.parent
    env_settings: dict[str, str] = {
        "DCS_PYLOT_DASH_LICENSE_FILE_PATH_OVERRIDE": str(repo_path / "LICENSE"),
        "DCS_PYLOT_DASH_PRIVACY_POLICY_FILE_PATH_OVERRIDE": str(repo_path / "privacy_policy.md"),
        "DCS_PYLOT_DASH_THIRD_PARTY_LICENSES_FILE_PATH_OVERRIDE": str(repo_path / "third_party_licenses.txt"),
        "DCS_PYLOT_DASH_TERMS_OF_SERVICE_FILE_PATH_OVERRIDE": str(repo_path / "terms_of_service.md"),
    }
    os.environ |= env_settings
    app = await DcsPylotDash.create_app()
    assert isinstance(app, FastAPI)
    assert app.routes

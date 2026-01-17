# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport, Response

from dcs_pylot_dash.api.api_model import APIExportModel
from dcs_pylot_dash.api.api_routes import APIRoutes
from dcs_pylot_dash.app import DcsPylotDash


@pytest.fixture
async def app() -> FastAPI:
    repo_path: Path = Path(__file__).parent.parent
    env_settings: dict[str, str] = {
        "DCS_PYLOT_DASH_LICENSE_FILE_PATH_OVERRIDE": str(repo_path / "LICENSE"),
        "DCS_PYLOT_DASH_PRIVACY_POLICY_FILE_PATH_OVERRIDE": str(repo_path / "privacy_policy.md"),
        "DCS_PYLOT_DASH_THIRD_PARTY_LICENSES_FILE_PATH_OVERRIDE": str(repo_path / "third_party_licenses.txt"),
        "DCS_PYLOT_DASH_TERMS_OF_SERVICE_FILE_PATH_OVERRIDE": str(repo_path / "terms_of_service.md"),
    }
    os.environ |= env_settings
    return await DcsPylotDash.create_app()


@pytest.fixture()
def app_client(app: FastAPI) -> AsyncClient:
    return AsyncClient(
        http2=True, base_url="http://localhost:8000" + DcsPylotDash.API_PATH, transport=ASGITransport(app=app)
    )


@pytest.mark.asyncio
async def test_app_routes(app: FastAPI) -> None:
    assert app.routes


async def test_generate(app_client: AsyncClient) -> None:
    response: Response = await app_client.get(APIRoutes.SAMPLE_MODEL)
    response.raise_for_status()
    api_export_model: APIExportModel = APIExportModel.model_validate(response.json())
    response = await app_client.post(APIRoutes.GENERATE, json=api_export_model.model_dump())
    response.raise_for_status()
    assert response.headers["Content-Type"] == "application/zip"

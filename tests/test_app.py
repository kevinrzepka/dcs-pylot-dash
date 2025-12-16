# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import os
from pathlib import Path

import pytest
from fastapi import FastAPI

from dcs_pylot_dash.app import DcsPylotDash


@pytest.mark.asyncio
async def test_app():
    os.environ["DCS_PYLOT_DASH_SETTINGS_FILE_PATH"] = str(
        (Path(__file__).parent / "data" / "test.env").resolve(strict=True)
    )
    app = await DcsPylotDash.create_app()
    assert isinstance(app, FastAPI)
    assert app.routes


def test_foo():
    assert 1 == 1

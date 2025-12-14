# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import pytest
from fastapi import FastAPI

from dcs_pylot_dash.app import DcsPylotDash


@pytest.mark.asyncio
async def test_app():
    app = await DcsPylotDash.create_app()
    assert isinstance(app, FastAPI)
    assert app.routes


def test_foo():
    assert 1 == 1

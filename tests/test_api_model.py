# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import pytest
from pydantic import ValidationError

from dcs_pylot_dash.api.api_model import APIColorScaleRange


def test_color_scale():
    with pytest.raises(ValidationError):
        APIColorScaleRange(from_value=0, to_value=100, color="#000000s")
        pytest.fail("Validation should have failed")

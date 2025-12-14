# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE

import pytest


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ([], None),
        ([""], None),
        (["", ""], None),
        (["", "", "test"], "test"),
        (["test", "", ""], "test"),
        (["", "test", ""], "test"),
        ([None], None),
        ([None, None], None),
        ([None, "test", None], "test"),
        (["test1", "test2"], "test1"),
        ([" "], " "),
    ],
)
def test_first_non_empty(test_input, expected):
    from dcs_pylot_dash.service.string_utils import StringUtils

    assert StringUtils.first_non_empty(*test_input) == expected

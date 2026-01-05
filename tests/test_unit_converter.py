# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import pytest

from dcs_pylot_dash.service.units import Unit, UnitConverter


@pytest.mark.parametrize(
    "src_unit,value,dst_unit,expected",
    [
        (Unit.METERS, 1000, Unit.MILES, 0.621371),
        (Unit.METERS, 1, Unit.FEET, 3.28084),
        (Unit.FEET, 100, Unit.METERS, 30.48),
        (Unit.MS, 10, Unit.MPH, 22.3694),
        (Unit.KMH, 100, Unit.MPH, 62.1371),
        (Unit.MPH, 62.1371, Unit.KMH, 100),
        (Unit.MPH, 1, Unit.FTS, 1.46667),
        (Unit.FTS, 1, Unit.MPH, 0.681818),
        (Unit.FTS, 1, Unit.KMH, 1.09728),
        (Unit.POUNDS, 10, Unit.KILOGRAMS, 4.53592),
        (None, 100, Unit.METERS, pytest.raises(ValueError)),
        (Unit.METERS, None, Unit.FEET, None),
        (Unit.METERS, 100, None, pytest.raises(ValueError)),
        (Unit.METERS, 100, Unit.METERS, 100),
        (Unit.RADIANS, 3.14159, Unit.DEGREES, 180),
        (Unit.DEGREES, 180, Unit.RADIANS, 3.14159),
    ],
)
def test_convert(src_unit: Unit, value: float | None, dst_unit: Unit, expected: float | None) -> None:
    if isinstance(expected, type(pytest.raises(Exception))):
        with expected as e:
            UnitConverter.convert(src_unit, value, dst_unit)
        assert e.type == expected.excinfo.type
    else:
        result = UnitConverter.convert(src_unit, value, dst_unit)
        assert result == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(
    "unit_set",
    [UnitConverter.SPEED_UNITS, UnitConverter.WEIGHT_UNITS, UnitConverter.DISTANCE_UNITS, UnitConverter.RAD_UNITS],
)
def test_get_convertable_units_in_same_set(unit_set: set[Unit]) -> None:
    for unit in unit_set:
        assert UnitConverter.get_convertable_units(unit) == unit_set

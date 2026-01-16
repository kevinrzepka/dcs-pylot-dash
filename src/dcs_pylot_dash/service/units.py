# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
import math
from collections import defaultdict
from enum import StrEnum, auto
from typing import Any, ClassVar, FrozenSet

LOGGER = logging.getLogger(__name__)


class Unit(StrEnum):
    NONE = auto()
    METERS = auto()
    MILES = auto()
    FEET = auto()
    MS = auto()
    KMH = auto()
    MPH = auto()
    FTS = auto()
    FTMIN = auto()
    KNOTS = auto()
    POUNDS = auto()
    RADIANS = auto()
    DEGREES = auto()
    SECONDS = auto()
    KILOGRAMS = auto()
    DELTA_T_S = auto()


class UnitLabels:

    default: dict[Unit, str] = {
        Unit.METERS: "m",
        Unit.MILES: "mi",
        Unit.FEET: "ft",
        Unit.MS: "m/s",
        Unit.KMH: "km/h",
        Unit.MPH: "mph",
        Unit.FTS: "ft/s",
        Unit.FTMIN: "ft/min",
        Unit.KNOTS: "kts",
        Unit.POUNDS: "lbs",
        Unit.RADIANS: "rad",
        Unit.DEGREES: "°",
        Unit.SECONDS: "s",
        Unit.KILOGRAMS: "kg",
        Unit.DELTA_T_S: "s",
    }


class UnitDisplayNames:

    default: dict[Unit, str] = {
        Unit.METERS: "meters",
        Unit.MILES: "nautical miles",
        Unit.FEET: "feet",
        Unit.MS: "meters per second",
        Unit.KMH: "kilometers per hour",
        Unit.MPH: "miles per hour",
        Unit.FTS: "feet per second",
        Unit.FTMIN: "feet per minute",
        Unit.KNOTS: "knots",
        Unit.POUNDS: "pounds",
        Unit.RADIANS: "radians",
        Unit.DEGREES: "degrees",
        Unit.SECONDS: "seconds",
        Unit.KILOGRAMS: "kilograms",
        Unit.DELTA_T_S: "delta seconds",
    }


class MissingConverterError(Exception):
    def __init__(self, src: Unit, dst: Unit) -> None:
        super().__init__(f"Missing converter from {src} to {dst}")


class UnitConverter:
    SPEED_UNITS: FrozenSet[Unit] = frozenset([Unit.MS, Unit.MPH, Unit.KMH, Unit.KNOTS, Unit.FTS, Unit.FTMIN])
    DISTANCE_UNITS: FrozenSet[Unit] = frozenset([Unit.METERS, Unit.MILES, Unit.FEET])
    RAD_UNITS: FrozenSet[Unit] = frozenset([Unit.RADIANS, Unit.DEGREES])
    WEIGHT_UNITS: FrozenSet[Unit] = frozenset([Unit.KILOGRAMS, Unit.POUNDS])

    # only used to build _factors
    _init_factors: ClassVar[dict[Unit, dict[Unit, float]]] = defaultdict(dict)

    _init_factors[Unit.METERS][Unit.MILES] = 0.000621371
    _init_factors[Unit.METERS][Unit.FEET] = 3.28084
    _init_factors[Unit.MS][Unit.MPH] = 2.23694
    _init_factors[Unit.MS][Unit.KMH] = 3.6
    _init_factors[Unit.MS][Unit.KNOTS] = 1.94384
    _init_factors[Unit.MS][Unit.FTS] = 3.28084
    _init_factors[Unit.MS][Unit.FTMIN] = 3.28084 / 60
    _init_factors[Unit.KILOGRAMS][Unit.POUNDS] = 2.20462
    _init_factors[Unit.RADIANS][Unit.DEGREES] = 180 / math.pi
    _init_factors[Unit.NONE][Unit.NONE] = 1

    @staticmethod
    def _build_factors(_init_factors: dict[Unit, dict[Unit, float]]):
        factors = {}
        # build 2-way factors
        for src, dsts in _init_factors.items():
            factors[src] = {}
            for dst, factor in dsts.items():
                factors[src][dst] = factor
                if dst not in factors:
                    factors[dst] = {}
                factors[dst][src] = 1 / factor

        # build n-way factors. Works as long as there is a common base unit within one unit group.
        # What does not work: A>B, B>C. What works: A>B, A>C
        for src, dsts in factors.items():
            for dst_0, factor in dsts.items():
                for dst_1 in dsts:
                    # convert "backwards" to src, then "forwards" to dst_1
                    factors[dst_0][dst_1] = factors[dst_0][src] * factors[src][dst_1]
        return factors

    _factors: ClassVar[dict[Unit, dict[Unit, float]]] = _build_factors(_init_factors)

    @classmethod
    def get_convertable_units(cls, src: Unit) -> set[Unit]:
        """
        :param src:
        :return: Units, to which the src can be converted
        """
        return set(cls._factors.get(src, {}).keys())

    @classmethod
    def get_conversion_factor(cls, src: Unit, dst: Unit) -> float | None:
        if src is None:
            raise ValueError("src cannot be None")
        if dst is None:
            raise ValueError("dst cannot be None")
        if src == dst:
            return 1

        factor: float | None = None
        source_factors: dict[Unit, float] = cls._factors[src]
        if len(source_factors) > 0:
            factor = source_factors.get(dst)
        return factor

    @classmethod
    def convert(cls, src: Unit, value: Any, dst: Unit) -> Any:
        if value is None:
            return None
        factor: float | None = cls.get_conversion_factor(src, dst)
        if factor is None:
            raise MissingConverterError(src, dst)
        return value * factor

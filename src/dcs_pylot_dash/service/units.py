# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
import math
from collections import defaultdict
from enum import StrEnum, auto
from typing import Any, ClassVar

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
        Unit.KNOTS: "kts",
        Unit.POUNDS: "lbs",
        Unit.RADIANS: "rad",
        Unit.DEGREES: "°",
        Unit.SECONDS: "s",
        Unit.KILOGRAMS: "kg",
        Unit.DELTA_T_S: "s",
    }


class MissingConverterError(Exception):
    def __init__(self, src: Unit, dst: Unit) -> None:
        super().__init__(f"Missing converter from {src} to {dst}")


class UnitConverter:
    _factors: ClassVar[dict[Unit, dict[Unit, float]]] = defaultdict(dict)

    _factors[Unit.METERS][Unit.MILES] = 0.000621371
    _factors[Unit.METERS][Unit.FEET] = 3.28084
    _factors[Unit.FEET][Unit.MILES] = 0.000189394
    _factors[Unit.MS][Unit.MPH] = 2.23694
    _factors[Unit.MS][Unit.KMH] = 1 / 3.6
    _factors[Unit.MS][Unit.KNOTS] = 1.94384
    _factors[Unit.KMH][Unit.MPH] = 0.621371
    _factors[Unit.FTS][Unit.MPH] = 0.681818
    _factors[Unit.FTS][Unit.KNOTS] = 0.592484
    _factors[Unit.KNOTS][Unit.MPH] = 1.15078
    _factors[Unit.KILOGRAMS][Unit.POUNDS] = 2.20462
    _factors[Unit.RADIANS][Unit.DEGREES] = 180 / math.pi

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

        if factor is None:
            # there might still be a converter for the other way around
            dst_factors: dict[Unit, float] = cls._factors[dst]
            if len(dst_factors) > 0:
                dst_factor: float | None = dst_factors.get(src)
                if dst_factor is not None:
                    factor = 1 / dst_factor

        return factor

    @classmethod
    def convert(cls, src: Unit, value: Any, dst: Unit) -> Any:
        if value is None:
            return None
        factor: float | None = cls.get_conversion_factor(src, dst)
        if factor is None:
            raise MissingConverterError(src, dst)
        return value * factor

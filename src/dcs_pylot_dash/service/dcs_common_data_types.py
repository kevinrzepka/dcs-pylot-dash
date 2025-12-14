# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from enum import StrEnum, auto

LOGGER = logging.getLogger(__name__)


class LoReturnType(StrEnum):
    """
    TODO: there are commands w/ multiple return types, like LoGetADIPitchBankYaw
    """

    TABLE = auto()
    LIST = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()

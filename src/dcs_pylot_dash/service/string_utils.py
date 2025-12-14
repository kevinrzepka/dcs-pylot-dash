# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE


class StringUtils:

    @staticmethod
    def is_empty(s: str) -> bool:
        return s is None or len(s) == 0

    @staticmethod
    def is_not_empty(s: str) -> bool:
        return not StringUtils.is_empty(s)

    @staticmethod
    def first_non_empty(*args: str) -> str | None:
        for arg in args:
            if StringUtils.is_not_empty(arg):
                return arg
        return None

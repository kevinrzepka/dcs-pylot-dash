# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from datetime import datetime


class ISO8601MicrosecondsFormatter(logging.Formatter):
    """
    %(asctime)s as RFC3339/ISO8601 in UTC with microseconds, e.g.:
      2026-01-26T10:27:31.123456Z
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt: datetime = datetime.fromtimestamp(record.created).astimezone()
        return dt.isoformat(timespec="microseconds")

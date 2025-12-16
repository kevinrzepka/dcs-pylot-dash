# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
import re
import subprocess
from re import Match
from subprocess import CompletedProcess
from typing import Final, Any

from pydantic import BaseModel

from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings


class AppMetadata(BaseModel):
    version: str
    build_date: str = "unknown_date"
    build_commit: str = "unknown_commit"


class AppMetadataService:

    LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

    _app_settings: DCSPylotDashAppSettings
    _app_metadata: AppMetadata

    def __init__(self, app_settings: DCSPylotDashAppSettings):
        self._app_settings = app_settings
        self._app_metadata = AppMetadata(
            version=self._app_settings.app_version,
        )

        try:
            output: CompletedProcess[str] = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
            )
            stdout: str = output.stdout.strip()
            regex_match: Match[str] | None = re.compile("([0-9a-f]+)").fullmatch(stdout)
            if regex_match is not None:
                commit_id: str | Any = regex_match.group(1)
                self.LOGGER.info(f"Git commit hash: {commit_id}")
                self._app_metadata.build_commit = commit_id
        except Exception as e:
            self.LOGGER.exception(f"Failed to get git commit hash: {e}")

    @property
    def metadata(self) -> AppMetadata:
        return self._app_metadata

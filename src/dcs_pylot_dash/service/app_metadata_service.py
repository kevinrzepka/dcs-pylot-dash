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
from pydantic_settings import SettingsConfigDict, BaseSettings

from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings


class BuildMetadata(BaseSettings):
    build_date: str | None = None
    build_commit: str | None = None

    model_config = SettingsConfigDict(env_prefix=DCSPylotDashAppSettings.ENV_PREFIX, extra="ignore")


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
        build_metadata: BuildMetadata = BuildMetadata()
        self._app_metadata = AppMetadata(
            version=self._app_settings.app_version,
            build_date=build_metadata.build_date,
            build_commit=build_metadata.build_commit,
        )

        if self._app_metadata.build_commit is None:
            self._app_metadata.build_commit = self.parse_git_commit_hash()

    def parse_git_commit_hash(self) -> str | None:
        try:
            output: CompletedProcess[str] = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
            )
            stdout: str = output.stdout.strip()
            regex_match: Match[str] | None = re.compile("([0-9a-f]+)").fullmatch(stdout)
            if regex_match is not None:
                commit_id: str | Any = regex_match.group(1)
                self.LOGGER.info(f"Git commit hash: {commit_id}")
                return commit_id
        except Exception as e:
            self.LOGGER.exception(f"Failed to get git commit hash: {e}")
            return None

    @property
    def metadata(self) -> AppMetadata:
        return self._app_metadata

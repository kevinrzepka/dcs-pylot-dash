# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class DCSPylotDashAppSettings(BaseSettings):
    ENV_PREFIX: ClassVar[str] = "DCS_PYLOT_DASH_"

    # path to populate DCSPylotDashAppSettings
    settings_file_path: str | None = None

    app_name: str = "DCSPylotDash"
    app_version: str = "v1.0.0"

    resources_dir: str | None = None

    mount_ui: bool = False
    # this directory is relative to (i.e., inside) the source package 'dcs_pylot_dash'
    ui_base_dir: str = "static/ui"
    ui_index_file_name: str = "index.html"

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore")

    @property
    def resources_dir_path(self) -> Path:
        return Path(self.resources_dir) if self.resources_dir is not None else None


class DCSPylotDashAppMetaSettings(BaseSettings):
    # path to populate DCSPylotDashAppSettings
    settings_file_path: str | None = None

    model_config = SettingsConfigDict(env_prefix=DCSPylotDashAppSettings.ENV_PREFIX)

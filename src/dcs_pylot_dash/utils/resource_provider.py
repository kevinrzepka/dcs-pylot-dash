# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from logging import Logger
from pathlib import Path
from typing import Final


class ResourceProvider:

    LOGGER: Final[Logger] = logging.getLogger(__name__)

    # repo 'dcs-pylot-dash' root dir
    RESOURCES_DIR_DEFAULT: Final[Path] = Path(__file__).parent.parent.parent.parent / "resources"

    TEMPLATES_DIR_NAME: Final[str] = "templates"
    EXTERNAL_MODELS_DIR_NAME: Final[str] = "external_models"
    SAMPLE_EXPORT_MODELS_DIR_NAME: Final[str] = "sample_export_models"
    NOTICES_DIR_NAME: Final[str] = "notices"

    resources_dir: Path = RESOURCES_DIR_DEFAULT

    def __init__(self, resources_dir: Path | None = None):
        self.resources_dir = resources_dir or self.RESOURCES_DIR_DEFAULT

    def read_file(self, file_path_str: str) -> str:
        file_path: Path = Path(file_path_str).resolve()
        self.LOGGER.info(f"Reading file: {file_path}")
        return file_path.read_text()

    def read_template_file(self, template_file_name: str) -> str:
        template_path = self.templates_dir / template_file_name
        self.LOGGER.info(f"Reading template file: {template_path}")
        return template_path.read_text()

    def read_external_model_file(self, model_file_name: str) -> str:
        external_model_path: Path = self.external_models_dir / model_file_name
        self.LOGGER.info(f"Reading external model file: {external_model_path}")
        return external_model_path.read_text()

    def read_sample_model_file(self, model_file_name: str) -> str:
        external_model_path: Path = self.sample_export_models_dir / model_file_name
        self.LOGGER.info(f"Reading external model file: {external_model_path}")
        return external_model_path.read_text()

    def read_notice(self, notice_file_name: str) -> str:
        notice_path: Path = self.notices_dir / notice_file_name
        self.LOGGER.info(f"Reading notice file: {notice_path}")
        return notice_path.read_text()

    def resolve_path_from_base(self, base_path: Path, relative_path: str) -> Path | None:
        full_path: Path = base_path / Path(relative_path)
        try:
            resolved_relative_path: Path = full_path.relative_to(base_path)
            resolved_path: Path = (base_path / resolved_relative_path).resolve()
            self.LOGGER.info(f"Resolved path '{relative_path}' from base path '{base_path}' to: {resolved_path}")
            return resolved_path
        except ValueError as e:
            self.LOGGER.warning(f"Could not resolve path '{relative_path}' from base path '{base_path}': {e}")
            return None

    @property
    def templates_dir(self) -> Path:
        return self.resources_dir / self.TEMPLATES_DIR_NAME

    @property
    def external_models_dir(self) -> Path:
        return self.resources_dir / self.EXTERNAL_MODELS_DIR_NAME

    @property
    def sample_export_models_dir(self) -> Path:
        return self.resources_dir / self.SAMPLE_EXPORT_MODELS_DIR_NAME

    @property
    def notices_dir(self) -> Path:
        return self.resources_dir / self.NOTICES_DIR_NAME

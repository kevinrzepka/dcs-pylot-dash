# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from logging import Logger
from pathlib import Path
from typing import Final


class ResourceProvider:

    LOGGER: Final[Logger] = logging.getLogger(__name__)

    RESOURCES_DIR_DEFAULT: Final[Path] = Path(__file__).parent.parent.parent.parent / "resources"

    TEMPLATES_DIR_NAME: Final[str] = "templates"
    EXTERNAL_MODELS_DIR_NAME: Final[str] = "external_models"
    SAMPLE_EXPORT_MODELS_DIR: Final[str] = "sample_export_models"

    resources_dir: Path = RESOURCES_DIR_DEFAULT

    def __init__(self, resources_dir: Path | None = None):
        self.resources_dir = resources_dir or self.RESOURCES_DIR_DEFAULT

    def read_template_file(self, template_name: str) -> str:
        template_path = self.templates_dir / template_name
        self.LOGGER.info(f"Reading template from: {template_path}")
        return template_path.read_text()

    def read_external_model_file(self, model_name: str) -> str:
        external_model_path: Path = self.external_models_dir / model_name
        self.LOGGER.info(f"Reading external model from: {external_model_path}")
        return external_model_path.read_text()

    @property
    def templates_dir(self) -> Path:
        return self.resources_dir / self.TEMPLATES_DIR_NAME

    @property
    def external_models_dir(self) -> Path:
        return self.resources_dir / self.EXTERNAL_MODELS_DIR_NAME

    @property
    def sample_export_models_dir(self) -> Path:
        return self.resources_dir / self.SAMPLE_EXPORT_MODELS_DIR

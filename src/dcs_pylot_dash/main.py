# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE

import asyncio
import logging.config
from logging import Logger
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI

from dcs_pylot_dash.app import DcsPylotDash


def main():
    """
    see https://uvicorn.dev/settings/#configuration-methods
    :return:
    """
    logger: Logger = logging.getLogger(__name__)
    logger.info("Starting DCS Pylot Dash")
    app: FastAPI = asyncio.run(DcsPylotDash.create_app())
    uvicorn.run(app, host="127.0.0.1")


if __name__ == "__main__":
    logging_config_path: Path = Path(__file__).parent / "logging.yaml"
    with logging_config_path.open() as f:
        logging.config.dictConfig(yaml.safe_load(f))
    main()

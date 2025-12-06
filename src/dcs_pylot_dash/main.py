#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE

import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from dcs_pylot_dash.app import DcsPylotDash


def main():
    """
    see https://uvicorn.dev/settings/#configuration-methods
    :return:
    """
    app: FastAPI = asyncio.run(DcsPylotDash.create_app())
    uvicorn.run(app, host="127.0.0.1")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

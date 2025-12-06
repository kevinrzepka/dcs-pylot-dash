#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE

from fastapi import FastAPI

from dcs_pylot_dash.api.main_router import MainRouter


class DcsPylotDash:

    @staticmethod
    async def create_app() -> FastAPI:
        fast_api: FastAPI = FastAPI()
        fast_api.include_router(await MainRouter.create_router())
        return fast_api

#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
from base64 import b64decode

from pydantic import BaseModel


class GithubLicenseInfo(BaseModel):
    key: str | None = None
    name: str | None = None
    spdx_id: str | None = None
    url: str | None = None


class GetLicenseResponse(BaseModel):
    url: str | None = None
    content: str | None = None
    encoding: str | None = None
    license: GithubLicenseInfo | None = None

    @property
    def plain_text(self) -> str | None:
        if self.encoding == 'base64':
            return b64decode(self.content.encode('utf-8')).decode('utf-8')
        return self.content

#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import logging
import time
from base64 import b64decode
from logging import Logger
from pathlib import Path

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
        if self.encoding == "base64":
            return b64decode(self.content.encode("utf-8")).decode("utf-8")
        return self.content


class GetLicenseResponseCacheEntry(BaseModel):
    response: GetLicenseResponse
    # epoch seconds, when the entry was obtained
    timestamp: float
    # version of the software with which this entry was created
    version: str = "1.0.0"


class GetLicenseResponseCacheContainer(BaseModel):
    entries: dict[str, GetLicenseResponseCacheEntry] = {}


class GetLicenseResponseCache:
    # key: url
    _container: GetLicenseResponseCacheContainer

    _LOGGER: Logger = logging.getLogger(__name__)

    FILE_NAME_DEFAULT = ".github-license-api-cache.json"

    def __init__(self):
        self._container = GetLicenseResponseCacheContainer()

    def put(self, url: str, response: GetLicenseResponse):
        self._container.entries[url] = GetLicenseResponseCacheEntry(response=response, timestamp=time.time())

    def get(self, url: str) -> GetLicenseResponse | None:
        entry: GetLicenseResponseCacheEntry | None = self._container.entries.get(url)
        if entry is not None:
            return entry.response
        return None

    def persist(self, file_path: Path | None = None) -> Path:
        file_path = file_path or Path(self.FILE_NAME_DEFAULT)
        self._LOGGER.info(f"persisting cache to {file_path}")
        file_path.write_text(self._container.model_dump_json(indent=2))
        return file_path

    def load(self, file_path: Path | None = None) -> None:
        file_path = file_path or Path(self.FILE_NAME_DEFAULT)
        self._LOGGER.info(f"loading cache from {file_path}")
        if file_path.exists():
            container_json_str: str = file_path.read_text()
            self._container = GetLicenseResponseCacheContainer.model_validate_json(container_json_str)
        else:
            self._LOGGER.info(f"cache file {file_path} does not exist")

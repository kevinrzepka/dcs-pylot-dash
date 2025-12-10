#  Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
#  SPDX-License-Identifier: MIT
#  License-Filename: LICENSE
import logging
import time
from base64 import b64decode
from logging import Logger
from pathlib import Path
from typing import Final

from pydantic import BaseModel

from sbom_to_oss_attrib.utils import SbomToAttributionError


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
    _LOGGER: Final[Logger] = logging.getLogger(__name__)

    # key: url
    _container: GetLicenseResponseCacheContainer
    _cache_file_path: Path | None

    def __init__(self, cache_file_path: Path | None = None):
        self._container = GetLicenseResponseCacheContainer()
        self._cache_file_path = cache_file_path

    def put(self, url: str, response: GetLicenseResponse):
        self._container.entries[url] = GetLicenseResponseCacheEntry(response=response, timestamp=time.time())

    def get(self, url: str) -> GetLicenseResponse | None:
        entry: GetLicenseResponseCacheEntry | None = self._container.entries.get(url)
        if entry is not None:
            return entry.response
        return None

    def persist(self) -> Path:
        if self._cache_file_path is None:
            raise SbomToAttributionError("cache file path is not set, cannot persist cache")
        self._LOGGER.info(f"persisting cache to {self._cache_file_path}")
        self._cache_file_path.write_text(self._container.model_dump_json(indent=2))
        return self._cache_file_path

    def load(self) -> None:
        self._LOGGER.info(f"loading cache from {self._cache_file_path}")
        if self._cache_file_path.exists():
            container_json_str: str = self._cache_file_path.read_text()
            self._container = GetLicenseResponseCacheContainer.model_validate_json(container_json_str)
        else:
            self._LOGGER.info(f"cache file {self._cache_file_path} does not exist")

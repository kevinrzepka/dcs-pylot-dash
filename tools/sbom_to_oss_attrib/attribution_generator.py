# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import json
import logging
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from httpx import AsyncClient, Response
from pydantic import BaseModel

from sbom_to_oss_attrib.cyclonedx_sbom import Sbom, SbomComponent
from sbom_to_oss_attrib.github_api import GetLicenseResponse, GetLicenseResponseCache
from sbom_to_oss_attrib.utils import StringUtils


class AttributionEntry(BaseModel):
    # full qualified name of the component
    name: str
    license_id: str
    version: str | None = None
    license_text: str | None = None
    homepage: str | None = None
    source: object = None


class Attribution(BaseModel):
    entries: list[AttributionEntry] = []


class OssAttributionGenerator:
    CACHE_FILE_PATH_DEFAULT: Final[Path] = Path(".github-license-api-cache.json").resolve()

    LOGGER: logging.Logger = logging.getLogger(__name__)

    _http_client: AsyncClient
    _github_rate_limit_exceeded: bool = False
    _get_license_cache: GetLicenseResponseCache | None
    _persist_cache: bool = True

    def __init__(
        self,
        github_api_token: str | None = None,
        cache_github_responses: bool = True,
        persist_cache: bool = True,
        cache_file_path: Path = CACHE_FILE_PATH_DEFAULT,
    ):
        headers: dict[str, str] = {}
        if github_api_token is not None:
            headers["Authorization"] = f"Bearer {github_api_token}"
        self._http_client = AsyncClient(headers=headers, follow_redirects=True)
        self._get_license_cache = GetLicenseResponseCache(cache_file_path) if cache_github_responses else None
        self._persist_cache = persist_cache

    def parse_sbom(self, input_file: Path) -> Sbom:
        self.LOGGER.info(f"Building OSS attribution for SBOM {input_file}")
        input_content_str: str = input_file.read_text()
        input_content_json: dict[str, Any] = json.loads(input_content_str)
        return Sbom.model_validate(input_content_json)

    async def _fetch_license_info_from_github(self, component: SbomComponent) -> GetLicenseResponse | None:
        license_url: str = component.probable_github_api_license_url
        cached_response: GetLicenseResponse | None = None
        if self._get_license_cache is not None:
            cached_response = self._get_license_cache.get(license_url)
        if cached_response is not None:
            return cached_response

        self.LOGGER.warning(f"GitHub API rate limit exceeded, skipping {component.qualified_name}")
        if self._github_rate_limit_exceeded:
            return None
        self.LOGGER.info(f"fetching license for {component.qualified_name} from {license_url}")
        response: Response = await self._http_client.get(license_url)
        try:
            if response.status_code == HTTPStatus.FORBIDDEN:
                self._github_rate_limit_exceeded = True
            response.raise_for_status()
            get_license_response: GetLicenseResponse = GetLicenseResponse.model_validate(response.json())
            if self._get_license_cache is not None:
                self._get_license_cache.put(license_url, get_license_response)
            return get_license_response
        except Exception as e:
            self.LOGGER.error(f"failed to load license from {license_url}: {e}", exc_info=True)

    async def build_attribution_entry_for_component(self, component: SbomComponent) -> AttributionEntry:
        license_text: str | None = component.probable_license_text
        license_id: str | None = component.accurate_or_probable_license_id
        # TODO: Could also be that the information is trash and github has better quality
        #  Could always fetch and also compare ID, to warn in case of  mismatch
        #  fallback: list all external ref urls
        if StringUtils.is_empty(license_text) or StringUtils.is_empty(license_id):
            if StringUtils.is_not_empty(component.probable_github_api_license_url):
                api_response: GetLicenseResponse | None = await self._fetch_license_info_from_github(component)
                if api_response is not None:
                    license_id = license_id or api_response.license.key
                    license_text = license_text or api_response.plain_text

        if StringUtils.is_empty(license_text) and StringUtils.is_empty(license_id):
            self.LOGGER.warning(f"Could not find any license information for {component.qualified_name}")

        return AttributionEntry(
            name=component.qualified_name,
            version=component.version,
            license_id=license_id or "UNKNOWN LICENSE ID",
            license_text=license_text or "UNKNOWN LICENSE TEXT",
            homepage=component.probable_website_url,
            source=component,
        )

    async def build_attribution(self, input_file: Path) -> Attribution:
        sbom: Sbom = self.parse_sbom(input_file)
        attribution: Attribution = Attribution()
        if self._get_license_cache is not None:
            self._get_license_cache.load()
        for c in sbom.library_components:
            entry: AttributionEntry = await self.build_attribution_entry_for_component(c)
            attribution.entries.append(entry)
        if self._get_license_cache is not None and self._persist_cache:
            self._get_license_cache.persist()
        return attribution

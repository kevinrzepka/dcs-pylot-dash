# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import json
import logging
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from httpx import AsyncClient, Response, HTTPStatusError
from pydantic import BaseModel

from sbom_to_oss_attrib.cyclonedx_sbom import SBOM, SBOMComponent
from sbom_to_oss_attrib.github_api import (
    GetLicenseResponse,
    GetLicenseResponseCache,
)
from sbom_to_oss_attrib.utils import StringUtils


class AttributionEntry(BaseModel):
    # full qualified name of the component
    name: str
    license_id: str
    version: str | None = None
    license_text: str | None = None
    homepage: str | None = None
    authors: str | None = None
    source: object = None


class Attribution(BaseModel):
    entries: list[AttributionEntry] = []


class OssAttributionGenerator:
    CACHE_FILE_PATH_DEFAULT: Final[Path] = Path(".github-license-api-cache.json")
    PNPM_NODE_MODULES_PATH_DEFAULT: Final[Path] = (
        Path(__file__).parent.parent.parent / "dcs-pylot-dash-ui" / "node_modules" / ".pnpm"
    )

    LOGGER: logging.Logger = logging.getLogger(__name__)

    _http_client: AsyncClient
    _github_rate_limit_exceeded: bool = False
    _get_license_cache: GetLicenseResponseCache | None
    _persist_cache: bool = True
    _pnpm_node_modules_path: Path = PNPM_NODE_MODULES_PATH_DEFAULT

    def __init__(
        self,
        github_api_token: str | None = None,
        cache_github_responses: bool = True,
        persist_cache: bool = True,
        cache_file_path: Path = CACHE_FILE_PATH_DEFAULT,
        _node_modules_path: Path = PNPM_NODE_MODULES_PATH_DEFAULT,
    ):
        headers: dict[str, str] = {}
        if github_api_token is not None:
            headers["Authorization"] = f"Bearer {github_api_token}"
        self._http_client = AsyncClient(headers=headers, follow_redirects=True)
        self._get_license_cache = GetLicenseResponseCache(cache_file_path) if cache_github_responses else None
        self._persist_cache = persist_cache

    def parse_sbom(self, input_file: Path) -> SBOM:
        self.LOGGER.info(f"Building OSS attribution for SBOM {input_file}")
        input_content_str: str = input_file.read_text()
        input_content_json: dict[str, Any] = json.loads(input_content_str)
        return SBOM.model_validate(input_content_json)

    async def _fetch_license_info_from_github(self, component: SBOMComponent) -> GetLicenseResponse | None:
        license_url: str = component.probable_github_api_license_url
        cached_response: GetLicenseResponse | None = None
        if self._get_license_cache is not None:
            cached_response = self._get_license_cache.get(license_url)
        if cached_response is not None:
            return cached_response

        if self._github_rate_limit_exceeded:
            self.LOGGER.warning(f"GitHub API rate limit exceeded, skipping {component.qualified_name}")
            return None
        self.LOGGER.info(f"fetching license for {component.qualified_name} from {license_url}")
        response: Response = await self._http_client.get(license_url)
        try:
            if response.status_code == HTTPStatus.FORBIDDEN:
                self._github_rate_limit_exceeded = True
            github_response: GetLicenseResponse | None = None
            if response.status_code == HTTPStatus.NOT_FOUND:
                github_response = GetLicenseResponse()
            elif response.status_code == HTTPStatus.OK:
                github_response = GetLicenseResponse.model_validate(response.json())

            if self._get_license_cache is not None and github_response is not None:
                self._get_license_cache.put(license_url, github_response)

            response.raise_for_status()
            return github_response
        except Exception as e:
            if isinstance(e, HTTPStatusError) and e.response.status_code == HTTPStatus.NOT_FOUND:
                self.LOGGER.warning(f"No GitHub license information found for component {component.qualified_name}")
            else:
                self.LOGGER.error(f"failed to load license from {license_url}: {e}", exc_info=True)
            return None

    def _fetch_license_text_from_pnpm_node_modules(self, component: SBOMComponent) -> str | None:
        if not self._pnpm_node_modules_path.exists():
            self.LOGGER.debug(
                f"node_modules directory {self._pnpm_node_modules_path} does not exist, skipping {component.qualified_name}"
            )
            return None

        # example: @types+trusted-types@2.0.7
        folder_name: str = ""
        if StringUtils.is_not_empty(component.group):
            folder_name += f"{component.group}+"
        folder_name += component.name
        if StringUtils.is_not_empty(component.version):
            folder_name += f"@{component.version}"

        # there are also these constructs with multiple components, where only the first could be a match:
        # @angular+cdk@21.0.6_@angular+common@21.0.8_@angular+core@21.0.8_@angular+compiler@21.0._86bd3254d156402248a8f88a47ee594b
        def _find_dir_starting_with_component() -> Path | None:
            for d in self._pnpm_node_modules_path.iterdir():
                if d.is_dir() and d.name.startswith(folder_name):
                    self.LOGGER.debug(f"found matching directory {d} for {component.qualified_name}")
                    dir_: Path = d / "node_modules"
                    if StringUtils.is_not_empty(component.group):
                        dir_ /= component.group
                    dir_ /= component.name
                    return dir_
            return None

        # example: dcs-pylot-dash-ui/node_modules/.pnpm/@types+trusted-types@2.0.7/node_modules/@types/trusted-types
        module_dir: Path | None = self._pnpm_node_modules_path / folder_name / "node_modules"
        if StringUtils.is_not_empty(component.group):
            module_dir /= component.group
        module_dir /= component.name

        if module_dir is not None and not module_dir.exists():
            module_dir = _find_dir_starting_with_component()

        if module_dir is not None and module_dir.exists():
            for p in module_dir.iterdir():
                if p.is_file(follow_symlinks=True) and p.stem.lower() == "license":
                    self.LOGGER.info(f"Reading license file {p} for {component.qualified_name}")
                    try:
                        return p.read_text()
                    except Exception as e:
                        self.LOGGER.error(f"failed to read license file {p}: {e}")
        return None

    async def build_attribution_entry_for_component(self, component: SBOMComponent) -> AttributionEntry:
        license_text: str | None = component.probable_license_text
        license_id: str | None = component.accurate_or_probable_license_id

        if StringUtils.is_empty(license_text):
            license_text = self._fetch_license_text_from_pnpm_node_modules(component)

        # TODO: Could also be that the information is trash and github has better quality
        #  Could always fetch and also compare ID, to warn in case of  mismatch
        #  fallback: list all external ref urls
        if StringUtils.is_empty(license_text) or StringUtils.is_empty(license_id):
            if StringUtils.is_not_empty(component.probable_github_api_license_url):
                api_response: GetLicenseResponse | None = await self._fetch_license_info_from_github(component)
                if api_response is not None and api_response.license is not None:
                    license_id = license_id or api_response.license.key
                    license_text = license_text or api_response.plain_text

        if StringUtils.is_empty(license_text) and StringUtils.is_empty(license_id):
            for l in component.licenses:
                if l.expression is not None:
                    self.LOGGER.info(f"Using expression {l.expression} as license text for {component.qualified_name}")
                    license_text = l.expression

        if StringUtils.is_empty(license_text) and StringUtils.is_empty(license_id):
            self.LOGGER.warning(f"Could not find any license information for {component.qualified_name}")

        return AttributionEntry(
            name=component.qualified_name,
            version=component.version,
            license_id=license_id or "UNKNOWN LICENSE ID",
            license_text=license_text,
            homepage=component.probable_website_url,
            authors=component.authors_str,
            source=component,
        )

    async def build_attribution(self, input_file: Path) -> Attribution:
        sbom: SBOM = self.parse_sbom(input_file)
        attribution: Attribution = Attribution()
        if self._get_license_cache is not None:
            self._get_license_cache.load()
        for c in sbom.library_or_framework_components:
            entry: AttributionEntry = await self.build_attribution_entry_for_component(c)
            attribution.entries.append(entry)
        if self._get_license_cache is not None and self._persist_cache:
            self._get_license_cache.persist()
        return attribution

# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
import logging
from base64 import b64decode
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field

from sbom_to_oss_attrib.utils import StringUtils


class SbomLicenseText(BaseModel):
    content: str
    content_type: str = Field(alias="contentType")
    encoding: str | None = None

    @property
    def plain_text(self) -> str | None:
        if self.encoding == "base64":
            return b64decode(self.content.encode("utf-8")).decode("utf-8")
        return self.content


class SbomLicense(BaseModel):
    name: str | None = None
    id: str | None = None
    url: str | None = None
    acknowledgement: str | None = None
    text: SbomLicenseText | None = None

    @property
    def has_id(self) -> bool:
        return StringUtils.is_not_empty(self.id)

    @property
    def has_url(self) -> bool:
        return StringUtils.is_not_empty(self.url)

    @property
    def has_text(self) -> bool:
        return self.text is not None and StringUtils.is_not_empty(self.text.plain_text)


class SbomLicenseContainer(BaseModel):
    license: SbomLicense


class ExternalReferenceType(StrEnum):
    VCS = "vcs"
    WEBSITE = "website"
    DOCUMENTATION = "documentation"
    ISSUE_TRACKER = "issue-tracker"
    RELEASE_NOTES = "release-notes"
    OTHER = "other"


class SbomExternalReference(BaseModel):
    url: str | None = None
    comment: str | None = None
    type: str | None = None

    @property
    def is_github(self) -> bool:
        return StringUtils.is_not_empty(self.url) and self.url.startswith("https://github.com/")

    @property
    def is_github_vcs(self) -> bool:
        return self.is_github and self.type == ExternalReferenceType.VCS

    @property
    def is_github_website(self) -> bool:
        return self.is_github and self.type == ExternalReferenceType.WEBSITE


class SbomComponent(BaseModel):
    LOGGER: ClassVar[logging.Logger] = logging.getLogger(__name__)

    bom_ref: str = Field(alias="bom-ref")
    component_type: str = Field(alias="type")
    # prefix for the full name
    group: str | None = None
    name: str
    # Components of type 'application', like 'pnpm-lock.yaml' may not have a version.
    version: str | None = None
    licenses: list[SbomLicenseContainer] = []
    external_references: list[SbomExternalReference] = Field(alias="externalReferences", default_factory=list)

    @property
    def qualified_name(self) -> str:
        return f"{self.group}.{self.name}" if self.group is not None else self.name

    @property
    def is_library(self) -> bool:
        return self.component_type == "library"

    @property
    def has_licenses(self) -> bool:
        return len(self.licenses) > 0

    @property
    def licenses_with_id(self) -> list[SbomLicense]:
        return [l.license for l in self.licenses if l.license.has_id]

    @property
    def licenses_with_text(self) -> list[SbomLicense]:
        return [l.license for l in self.licenses if l.license.has_text]

    @property
    def accurate_or_probable_license_id(self) -> str | None:
        return self.license_id or self.probable_license_id_from_text

    @property
    def license_id(self) -> str | None:
        licenses_with_id: list[SbomLicense] = self.licenses_with_id
        distinct_license_ids: set[str] = {l.id for l in licenses_with_id}
        if len(distinct_license_ids) == 0:
            return None
        elif len(distinct_license_ids) > 1:
            self.LOGGER.warning(
                f"Component {self.qualified_name} has multiple licenses with different IDs: {licenses_with_id}. IDs: {distinct_license_ids}."
            )
        return licenses_with_id[0].id

    @property
    def probable_license_id_from_text(self) -> str | None:
        """
        :return: The shortest license text, if any.
        """
        licenses_with_text: list[SbomLicense] = self.licenses_with_text
        licenses_with_text.sort(key=lambda l: len(l.text.plain_text))
        if len(licenses_with_text) > 0 and len(licenses_with_text[0].text.plain_text) < 100:
            return licenses_with_text[0].id
        return None

    @property
    def probable_license_text(self) -> str | None:
        """
        :return: The longest license text, if any.
        """
        licenses_with_text: list[SbomLicense] = self.licenses_with_text
        licenses_with_text.sort(key=lambda l: len(l.text.plain_text), reverse=True)
        if len(licenses_with_text) > 0:
            return licenses_with_text[0].text.plain_text
        return None

    @property
    def probable_website_url(self) -> str | None:
        website_urls: list[str] = [
            ref.url for ref in self.external_references if ref.type == ExternalReferenceType.WEBSITE
        ]
        website_urls.sort(key=lambda u: len(u))
        if len(website_urls) > 0:
            return website_urls[0]

        if len(self.github_urls) > 0:
            return self.github_urls[0]

        if len(self.external_references) > 0:
            return self.external_references[0].url

        return None

    @property
    def github_urls(self) -> list[str]:
        github_urls: list[str] = [ref.url for ref in self.external_references if ref.is_github]
        github_urls.sort(key=lambda u: len(u))
        return github_urls

    @property
    def probable_github_repo_url(self) -> str | None:
        github_vcs_urls: list[str] = [ref.url for ref in self.external_references if ref.is_github_vcs]
        github_vcs_urls.sort(key=lambda u: len(u))
        if len(github_vcs_urls) > 0:
            return github_vcs_urls[0]

        github_website_urls: list[str] = [ref.url for ref in self.external_references if ref.is_github_website]
        github_website_urls.sort(key=lambda u: len(u))
        if len(github_website_urls) > 0:
            return github_website_urls[0]

        if len(self.github_urls) > 0:
            return self.github_urls[0]

        return None

    @property
    def probable_github_api_url(self) -> str | None:
        probable_repo_url: str | None = self.probable_github_repo_url
        if probable_repo_url is None:
            return None
        repo_path: str = probable_repo_url.split("https://github.com/")[-1]
        chunks: list[str] = repo_path.split("/")
        if len(chunks) < 2:
            return None
        return f"https://api.github.com/repos/{chunks[0]}/{chunks[1]}"

    @property
    def probable_github_api_license_url(self) -> str | None:
        if self.probable_github_api_url is None:
            return None
        return f"{self.probable_github_api_url}/license"


class Sbom(BaseModel):
    components: list[SbomComponent] = []

    @property
    def library_components(self) -> list[SbomComponent]:
        return [c for c in self.components if c.is_library]

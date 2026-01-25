# Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
from typing import ClassVar

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from dcs_pylot_dash.app_settings import DCSPylotDashAppSettings
from dcs_pylot_dash.utils.resource_provider import ResourceProvider


class NoticesContainer(BaseModel):
    third_party_licenses_txt: str
    license_txt: str
    privacy_policy_md: str
    terms_of_service_md: str


class NoticesSettings(BaseSettings):
    THIRD_PARTY_LICENSES_FILE_NAME: ClassVar[str] = "third_party_licenses_distributed.txt"
    LICENSE_FILE_NAME: ClassVar[str] = "LICENSE"
    PRIVACY_POLICY_FILE_NAME: ClassVar[str] = "privacy_policy.md"
    TERMS_OF_SERVICE_FILE_NAME: ClassVar[str] = "terms_of_service.md"

    license_file_path_override: str | None = None
    privacy_policy_file_path_override: str | None = None
    terms_of_service_file_path_override: str | None = None
    third_party_licenses_file_path_override: str | None = None

    model_config = SettingsConfigDict(env_prefix=DCSPylotDashAppSettings.ENV_PREFIX, extra="ignore")


class NoticesService:

    _settings: NoticesSettings
    _resource_provider: ResourceProvider
    _notices: NoticesContainer

    def __init__(self, settings: NoticesSettings, resource_provider: ResourceProvider):
        self._resource_provider = resource_provider
        self._settings = settings
        self._notices = self.load_notices()

    def load_notices(self) -> NoticesContainer:
        third_party_licenses_txt: str = (
            self._resource_provider.read_notice(self._settings.THIRD_PARTY_LICENSES_FILE_NAME)
            if self._settings.third_party_licenses_file_path_override is None
            else self._resource_provider.read_file(self._settings.third_party_licenses_file_path_override)
        )
        license_txt: str = (
            self._resource_provider.read_notice(self._settings.LICENSE_FILE_NAME)
            if self._settings.license_file_path_override is None
            else self._resource_provider.read_file(self._settings.license_file_path_override)
        )
        privacy_policy_md: str = (
            self._resource_provider.read_notice(self._settings.PRIVACY_POLICY_FILE_NAME)
            if self._settings.privacy_policy_file_path_override is None
            else self._resource_provider.read_file(self._settings.privacy_policy_file_path_override)
        )
        terms_of_service_md: str = (
            self._resource_provider.read_notice(self._settings.TERMS_OF_SERVICE_FILE_NAME)
            if self._settings.terms_of_service_file_path_override is None
            else self._resource_provider.read_file(self._settings.terms_of_service_file_path_override)
        )
        return NoticesContainer(
            third_party_licenses_txt=third_party_licenses_txt,
            license_txt=license_txt,
            privacy_policy_md=privacy_policy_md,
            terms_of_service_md=terms_of_service_md,
        )

    @property
    def notices(self) -> NoticesContainer:
        return self._notices

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
export type APIUnit = {
  display_name: string;
  unit_id: string;
  symbol: string;
};

export type APISourceField = {
  display_name: string;
  field_id: string;
  default_unit_id: string;
  available_unit_ids: string[];
};

export type APISourceModel = {
  units: APIUnit[];
  fields: APISourceField[];
};

export type APINotices = {
  third_party_licenses_txt: string;
  license_txt: string;
  privacy_policy_md: string;
  terms_of_service_md: string;
};

export type APIAppMetadata = {
  version: string;
  build_date: string;
  build_commit: string;
};

export type APIExportField = {
  display_name: string;
  field_id: string;
  unit_id: string;
};

export type APIExportRow = {
  fields: APIExportField[];
};

export type APIExportModel = {
  rows: APIExportRow[];
  advanced_settings: APIExportModelAdvancedSettings | null;
};

export class AdvancedSettingsDefaults {
  static readonly LUA_BIND_ADDRESS: string = '127.0.0.1';
  static readonly LUA_BIND_PORT: number = 52025;
  static readonly POLL_INTERVAL_MS: number = 200;
}

export class AdvancedSettingsConstraints {
  static readonly LUA_BIND_PORT_MIN: number = 49152;
  static readonly LUA_BIND_PORT_MAX: number = 65535;

  static readonly POLL_INTERVAL_MS_MIN: number = 100;
  static readonly POLL_INTERVAL_MS_MAX: number = 1000;
}

export type APIExportModelAdvancedSettings = {
  lua_bind_address: string | null;
  lua_bind_port: number | null;
  poll_interval_ms: number | null;
};

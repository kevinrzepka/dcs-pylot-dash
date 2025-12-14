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

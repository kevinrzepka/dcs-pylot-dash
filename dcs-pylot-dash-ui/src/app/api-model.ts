/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
export type APIUnit = {
  displayName: string;
  unitId: string;
  symbol: string;
};

export type APISourceField = {
  displayName: string;
  internalName: string;
  defaultUnitId: string;
  availableUnitIds: string[];
};

export type APISourceModel = {
  units: APIUnit[];
  fields: APISourceField[];
};

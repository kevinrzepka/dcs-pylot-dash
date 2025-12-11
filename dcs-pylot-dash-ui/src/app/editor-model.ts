/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
export class DataPoint {
  displayName: string;
  internalFieldName: string;
  row: number;
  column: number;
  outputUnit: string | null;

  constructor(
    displayName: string,
    internalFieldName: string,
    row: number,
    column: number,
    outputUnitOverride: string | null = null,
  ) {
    this.displayName = displayName;
    this.internalFieldName = internalFieldName;
    this.row = row;
    this.column = column;
    this.outputUnit = outputUnitOverride;
  }
}

export class SourceDataPoint {
  displayName: string;
  internalFieldName: string;
  defaultUnit: DataPointUnit;
  availableUnits: DataPointUnit[];

  constructor(
    displayName: string,
    internalFieldName: string,
    defaultUnit: DataPointUnit,
    availableUnits: DataPointUnit[],
  ) {
    this.displayName = displayName;
    this.internalFieldName = internalFieldName;
    this.defaultUnit = defaultUnit;
    this.availableUnits = availableUnits;
  }
}

export class DataPointUnit {
  displayName: string;
  internalName: string;
  symbol: string;

  constructor(displayName: string, internalName: string, symbol: string) {
    this.displayName = displayName;
    this.internalName = internalName;
    this.symbol = symbol;
  }
}

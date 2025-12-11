/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
class DataPoint {
  displayName: string;
  internalFieldName: string;
  row: number;
  column: number;
  outputUnitOverride: string | null;

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
    this.outputUnitOverride = outputUnitOverride;
  }
}

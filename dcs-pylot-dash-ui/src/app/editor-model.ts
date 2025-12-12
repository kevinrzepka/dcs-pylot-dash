/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */

export class EditorModel {
  dataPointRows: DataPointRow[] = [];
}

export class DataPointRow {
  dataPoints: DataPoint[] = [];

  get lastColumnIndex(): number {
    return this.dataPoints.length - 1;
  }

  get nextColumnIndex(): number {
    return this.lastColumnIndex + 1;
  }

  public addDataPoint(dataPoint: DataPoint) {
    this.dataPoints.push(dataPoint);
  }

  public removeDataPoint(dataPoint: DataPoint) {
    this.dataPoints = this.dataPoints.filter((dp) => dp !== dataPoint);
  }
}

export class DataPoint {
  displayName: string;
  sourceDataPoint: SourceDataPoint;
  outputUnitId: string | null;

  constructor(
    displayName: string,
    sourceDataPoint: SourceDataPoint,
    outputUnitId: string | null = null,
  ) {
    this.displayName = displayName;
    this.sourceDataPoint = sourceDataPoint;
    this.outputUnitId = outputUnitId;
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

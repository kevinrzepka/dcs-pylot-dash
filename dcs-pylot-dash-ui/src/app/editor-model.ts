/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */

export class EditorModel {
  dataPointRows: DataPointRow[] = [];

  isEmpty(): boolean {
    return (
      this.dataPointRows.length === 0 ||
      this.dataPointRows.every((row: DataPointRow) => row.dataPoints.length === 0)
    );
  }
}

export class DataPointRow {
  dataPoints: DataPoint[] = [];

  get lastColumnIndex(): number {
    return this.dataPoints.length - 1;
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
  outputUnit: DataPointUnit;

  constructor(
    displayName: string,
    sourceDataPoint: SourceDataPoint,
    outputUnit: DataPointUnit | null = null,
  ) {
    this.displayName = displayName;
    this.sourceDataPoint = sourceDataPoint;
    this.outputUnit = outputUnit ? outputUnit : sourceDataPoint.defaultUnit;
  }

  public setOutputUnit(unit: DataPointUnit) {
    this.outputUnit = unit;
  }
}

export class SourceDataPoint {
  displayName: string;
  internalName: string;
  defaultUnit: DataPointUnit;
  availableUnits: DataPointUnit[];

  constructor(
    displayName: string,
    internalName: string,
    defaultUnit: DataPointUnit,
    availableUnits: DataPointUnit[],
  ) {
    this.displayName = displayName;
    this.internalName = internalName;
    this.defaultUnit = defaultUnit;
    this.availableUnits = availableUnits;
  }
}

export class DataPointUnit {
  displayName: string;
  unitId: string;
  symbol: string;

  constructor(displayName: string, unitId: string, symbol: string) {
    this.displayName = displayName;
    this.unitId = unitId;
    this.symbol = symbol;
  }
}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Button } from 'primeng/button';
import { DataPointEditor } from '../data-point-editor/data-point-editor';
import { DataPoint } from '../editor-model';
import { Card } from 'primeng/card';

export class DataPointRow {
  dataPoints: DataPoint[] = [];
  rowIndex: number = 0;

  constructor(rowIndex: number) {
    this.rowIndex = rowIndex;
  }

  get lastColumnIndex(): number {
    return this.dataPoints.length - 1;
  }

  get nextColumnIndex(): number {
    return this.lastColumnIndex + 1;
  }

  public addDataPoint(dataPoint: DataPoint) {
    dataPoint.row = this.rowIndex;
    dataPoint.column = this.nextColumnIndex;
    this.dataPoints.push(dataPoint);
  }

  public removeDataPoint(dataPoint: DataPoint) {
    this.dataPoints = this.dataPoints.filter((dp) => dp !== dataPoint);
    this.restoreIndices();
  }

  public restoreIndices() {
    this.dataPoints.forEach((value: DataPoint, index: number) => {
      value.column = index;
    });
  }
}

@Component({
  selector: 'app-editor-page',
  imports: [Button, DataPointEditor, Card],
  templateUrl: './editor-page.html',
  styleUrl: './editor-page.css',
})
export class EditorPage {
  dataPointRows: DataPointRow[] = [];

  addDataPointRow() {
    this.dataPointRows.push(new DataPointRow(this.dataPointRows.length));
  }

  addDataPoint(dataPointRow: DataPointRow) {
    const dataPoint: DataPoint = new DataPoint('New Data Point', 'new_data_point', 0, 0);
    dataPointRow.addDataPoint(dataPoint);
  }

  removeDataPoint(dataPointRow: DataPointRow, dataPoint: DataPoint) {
    dataPointRow.removeDataPoint(dataPoint);
  }
}

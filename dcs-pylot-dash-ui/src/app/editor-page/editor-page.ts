/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Button } from 'primeng/button';
import { DataPointEditor } from '../data-point-editor/data-point-editor';
import { DataPoint, DataPointRow } from '../editor-model';
import { Card } from 'primeng/card';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDragPlaceholder,
  CdkDropList,
  CdkDropListGroup,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';

@Component({
  selector: 'app-editor-page',
  imports: [
    Button,
    DataPointEditor,
    Card,
    CdkDrag,
    CdkDropList,
    CdkDragPlaceholder,
    CdkDropListGroup,
  ],
  templateUrl: './editor-page.html',
  styleUrl: './editor-page.css',
})
export class EditorPage {
  dataPointRows: DataPointRow[] = [];

  addDataPointRow() {
    this.dataPointRows.push(new DataPointRow());
  }

  addDataPoint(dataPointRow: DataPointRow) {
    const dataPoint: DataPoint = new DataPoint('New Data Point', 'new_data_point');
    dataPointRow.addDataPoint(dataPoint);
  }

  removeDataPoint(dataPointRow: DataPointRow, dataPoint: DataPoint) {
    dataPointRow.removeDataPoint(dataPoint);
  }

  protected dataPointDropped(event: CdkDragDrop<any, any>) {
    console.log('dataPointDropped', event);
    const previousDataPointRow: DataPointRow = event.previousContainer.data;
    const currentDataPointRow: DataPointRow = event.container.data;
    if (previousDataPointRow === currentDataPointRow) {
      if (event.previousIndex !== event.currentIndex) {
        moveItemInArray(previousDataPointRow.dataPoints, event.previousIndex, event.currentIndex);
      }
    } else {
      transferArrayItem(
        previousDataPointRow.dataPoints,
        currentDataPointRow.dataPoints,
        event.previousIndex,
        event.currentIndex,
      );
    }
  }
}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Button } from 'primeng/button';
import { DataPointEditor } from '../data-point-editor/data-point-editor';
import { DataPoint, DataPointRow, SourceDataPoint } from '../editor-model';
import { Card } from 'primeng/card';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDragHandle,
  CdkDragPlaceholder,
  CdkDropList,
  CdkDropListGroup,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { SourceDataPointService } from '../source-data-point-service';
import { SourceDataPointChooser } from '../source-data-point-chooser/source-data-point-chooser';
import { Tooltip } from 'primeng/tooltip';

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
    CdkDragHandle,
    SourceDataPointChooser,
    Tooltip,
  ],
  templateUrl: './editor-page.html',
  styleUrl: './editor-page.css',
})
export class EditorPage {
  dataPointRows: DataPointRow[] = [];

  constructor(private sourceDataPointService: SourceDataPointService) {}

  protected removeDataPointRow(dataPointRow: DataPointRow) {
    this.dataPointRows = this.dataPointRows.filter((row: DataPointRow) => row !== dataPointRow);
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

  protected dataPointRowDropped(event: CdkDragDrop<any, any>) {
    if (event.previousIndex !== event.currentIndex) {
      moveItemInArray(this.dataPointRows, event.previousIndex, event.currentIndex);
    }
  }

  protected addDataPointInRow(
    sourceDataPoint: SourceDataPoint | null,
    dataPointRow: DataPointRow | null = null,
  ) {
    if (sourceDataPoint) {
      const dataPoint: DataPoint = new DataPoint(sourceDataPoint.displayName, sourceDataPoint);
      if (dataPointRow !== null) {
        dataPointRow.addDataPoint(dataPoint);
      } else {
        const dataPointRow: DataPointRow = new DataPointRow();
        dataPointRow.addDataPoint(dataPoint);
        this.dataPointRows.push(dataPointRow);
      }
    }
  }
}

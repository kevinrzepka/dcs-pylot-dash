/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { ChangeDetectorRef, Component } from '@angular/core';
import { Button, ButtonDirective } from 'primeng/button';
import { DataPointEditor } from '../data-point-editor/data-point-editor';
import { DataPoint, DataPointRow, EditorModel, SourceDataPoint } from '../editor-model';
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
import { SourceDataPointChooser } from '../source-data-point-chooser/source-data-point-chooser';
import { Tooltip } from 'primeng/tooltip';
import { GeneratorService } from '../generator-service';
import { ReactiveFormsModule } from '@angular/forms';

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
    ButtonDirective,
    ReactiveFormsModule,
  ],
  templateUrl: './editor-page.html',
  styleUrl: './editor-page.css',
})
export class EditorPage {
  readonly NO_DATA_TOOLTIP: string = 'Add at least one data point to the dashboard.';

  protected generateButtonEnabled: boolean = false;
  protected generateButtonTooltip: string = this.NO_DATA_TOOLTIP;

  protected downloadButtonEnabled: boolean = false;
  protected downloadUrl: string | null = null;
  protected downloadFilename: string | null = 'dcs-pylot-dash-generated.zip';

  protected editorModel: EditorModel = new EditorModel();

  constructor(
    private generatorService: GeneratorService,
    private cdr: ChangeDetectorRef,
  ) {}

  protected generate() {
    this.generateButtonEnabled = false;
    this.downloadButtonEnabled = false;
    this.generatorService.generate(this.editorModel).subscribe((blob) => {
      if (blob) {
        this.downloadUrl = window.URL.createObjectURL(blob);
        this.downloadButtonEnabled = true;
      }
      this.generateButtonEnabled = true;
      this.cdr.detectChanges();
    });
    this.cdr.detectChanges();
  }

  protected removeDataPointRow(dataPointRow: DataPointRow) {
    this.editorModel.dataPointRows = this.editorModel.dataPointRows.filter(
      (row: DataPointRow) => row !== dataPointRow,
    );
    this.disableOrEnabledBuildButtonDependingOnModelEmpty();
  }

  protected removeDataPoint(dataPointRow: DataPointRow, dataPoint: DataPoint) {
    dataPointRow.removeDataPoint(dataPoint);
    this.disableOrEnabledBuildButtonDependingOnModelEmpty();
  }

  protected disableOrEnabledBuildButtonDependingOnModelEmpty(): void {
    if (this.editorModel.isEmpty()) {
      this.generateButtonTooltip = this.NO_DATA_TOOLTIP;
      this.generateButtonEnabled = false;
    } else {
      this.generateButtonTooltip = '';
      this.generateButtonEnabled = true;
    }
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
      moveItemInArray(this.editorModel.dataPointRows, event.previousIndex, event.currentIndex);
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
        this.editorModel.dataPointRows.push(dataPointRow);
      }
      this.disableOrEnabledBuildButtonDependingOnModelEmpty();
    }
  }
}

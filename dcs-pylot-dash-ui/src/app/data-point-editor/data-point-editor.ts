/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Card } from 'primeng/card';
import { FormsModule } from '@angular/forms';
import { InputText } from 'primeng/inputtext';
import { DataPoint, SourceDataPoint } from '../editor-model';
import { IftaLabel } from 'primeng/iftalabel';
import { Button } from 'primeng/button';
import { SourceDataPointChooser } from '../source-data-point-chooser/source-data-point-chooser';
import { Tooltip } from 'primeng/tooltip';

@Component({
  selector: 'app-data-point-editor',
  imports: [Card, FormsModule, InputText, IftaLabel, Button, SourceDataPointChooser, Tooltip],
  templateUrl: './data-point-editor.html',
  styleUrl: './data-point-editor.css',
})
export class DataPointEditor {
  @Output()
  onDeleteDataPoint: EventEmitter<DataPoint> = new EventEmitter<DataPoint>();

  @Input()
  dataPoint!: DataPoint;

  constructor() {}

  protected deleteDataPoint() {
    this.onDeleteDataPoint.emit(this.dataPoint);
  }

  protected handleSourceDataPointChange(sourceDataPoint: SourceDataPoint | null) {
    if (sourceDataPoint) {
      this.dataPoint.sourceDataPoint = sourceDataPoint;
      this.dataPoint.outputUnit = sourceDataPoint.defaultUnit;
    }
  }
}

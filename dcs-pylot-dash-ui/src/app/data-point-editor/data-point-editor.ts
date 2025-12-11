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
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { SourceDataPointService } from '../source-data-point-service';
import { Button } from 'primeng/button';
import { Tooltip } from 'primeng/tooltip';

@Component({
  selector: 'app-data-point-editor',
  imports: [Card, FormsModule, InputText, IftaLabel, AutoComplete, Button, Tooltip],
  templateUrl: './data-point-editor.html',
  styleUrl: './data-point-editor.css',
})
export class DataPointEditor {
  @Output()
  onDeleteDataPoint: EventEmitter<DataPoint> = new EventEmitter<DataPoint>();

  @Input()
  dataPoint!: DataPoint;
  protected sourceDataPoint: SourceDataPoint | undefined = undefined;
  protected sourceDataPointSuggestions: SourceDataPoint[] = [];

  constructor(private sourceDataPointService: SourceDataPointService) {}

  protected searchSourceDataPoints(event: AutoCompleteCompleteEvent) {
    let query: string | undefined = event.query;
    if (!query) {
      query = '';
    }
    this.sourceDataPointService.sourceDataPoints.subscribe((next: SourceDataPoint[]) => {
      this.sourceDataPointSuggestions = next.filter((sourceDataPoint: SourceDataPoint) =>
        sourceDataPoint.displayName.toLowerCase().includes(query.toLowerCase()),
      );
    });
  }

  protected deleteDataPoint() {
    this.onDeleteDataPoint.emit(this.dataPoint);
  }
}

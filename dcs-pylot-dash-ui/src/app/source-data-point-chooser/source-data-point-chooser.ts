/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SourceDataPoint } from '../editor-model';
import { SourceDataPointService } from '../source-data-point-service';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { IftaLabel } from 'primeng/iftalabel';
import { Tooltip } from 'primeng/tooltip';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

/**
 * This would be better as a select, but that currently does not support clearing the value after selection
 */
@Component({
  selector: 'app-source-data-point-chooser',
  imports: [AutoComplete, IftaLabel, Tooltip, ReactiveFormsModule],
  templateUrl: './source-data-point-chooser.html',
  styleUrl: './source-data-point-chooser.css',
})
export class SourceDataPointChooser implements OnInit {
  @Input()
  clearAfterEmit: boolean = false;

  @Input()
  restoreLabelOnBlur: boolean = true;

  @Input()
  label: string = 'Source Data Point';

  @Input()
  tooltip: string | null = null;

  @Input()
  initialValue: SourceDataPoint | null = null;

  @Output()
  protected onSourceDataPointChange: EventEmitter<SourceDataPoint | null> =
    new EventEmitter<SourceDataPoint | null>();

  fcSourceDataPoint: FormControl<SourceDataPoint | null>;

  lastSelectedSourceDataPoint: SourceDataPoint | null = null;

  protected sourceDataPointSuggestions: SourceDataPoint[] = [];

  @Input() disabled!: boolean;

  constructor(private sourceDataPointService: SourceDataPointService) {
    this.fcSourceDataPoint = new FormControl(null);
  }

  ngOnInit(): void {
    if (this.initialValue) {
      this.lastSelectedSourceDataPoint = this.initialValue;
      this.fcSourceDataPoint.setValue(this.initialValue);
    }
    this.fcSourceDataPoint.valueChanges.subscribe((value: SourceDataPoint | null) => {
      if (value) {
        if (this.lastSelectedSourceDataPoint !== value) {
          this.lastSelectedSourceDataPoint = value;
          this.onSourceDataPointChange.emit(value);
          if (this.clearAfterEmit) {
            this.lastSelectedSourceDataPoint = null;
            this.fcSourceDataPoint.setValue(null);
          }
        }
      } else if (
        this.lastSelectedSourceDataPoint !== null &&
        this.restoreLabelOnBlur &&
        !this.clearAfterEmit
      ) {
        this.fcSourceDataPoint.setValue(this.lastSelectedSourceDataPoint);
      }
    });
  }

  protected searchSourceDataPoints(event: AutoCompleteCompleteEvent) {
    let query: string | undefined = event.query;
    if (!query) {
      query = '';
    }
    this.sourceDataPointService.sourceDataPoints.subscribe((next: SourceDataPoint[]) => {
      this.sourceDataPointSuggestions = next.filter(
        (sourceDataPoint: SourceDataPoint) =>
          sourceDataPoint.displayName.toLowerCase().includes(query.toLowerCase()) ||
          sourceDataPoint.internalName.toLowerCase().includes(query?.toLowerCase()),
      );
    });
  }
}

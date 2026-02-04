/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import {
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChildren,
} from '@angular/core';
import { ColorScale, ColorScaleRange, DataPoint } from '../editor-model';
import { ColorScaleEntry } from '../color-scale-entry/color-scale-entry';
import { Button } from 'primeng/button';
import { Tooltip } from 'primeng/tooltip';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { IftaLabel } from 'primeng/iftalabel';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { EditorModelService } from '../editor-model-service';

@Component({
  selector: 'app-color-scale-editor',
  imports: [ColorScaleEntry, Button, Tooltip, AutoComplete, IftaLabel, ReactiveFormsModule],
  templateUrl: './color-scale-editor.html',
  styleUrl: './color-scale-editor.css',
})
export class ColorScaleEditor implements OnInit {
  @Input()
  dataPoint!: DataPoint;

  /**
   * Emits {@link dataPoint.colorScale} when its color scale changes.
   */
  @Output()
  colorScaleChanged: EventEmitter<ColorScale> = new EventEmitter<ColorScale>();

  @Output()
  closeDesired: EventEmitter<void> = new EventEmitter<void>();

  @ViewChildren(ColorScaleEntry)
  colorScaleEntries: ColorScaleEntry[] = [];

  protected fcCopyFromDataPoint: FormControl<DataPoint | null> = new FormControl(null);
  protected copyFromDataPointSuggestions: DataPoint[] = [];

  constructor(
    private editorModelService: EditorModelService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.ranges.push(new ColorScaleRange());
  }

  protected get ranges(): ColorScaleRange[] {
    return this.dataPoint.colorScale.ranges;
  }

  protected set ranges(ranges: ColorScaleRange[]) {
    this.dataPoint.colorScale.ranges = ranges;
  }

  protected get sortedColorScaleEntries(): ColorScaleEntry[] {
    return this.ranges
      .map((range: ColorScaleRange) =>
        this.colorScaleEntries.find((entry) => entry.range === range),
      )
      .filter((entry) => entry !== undefined);
  }

  protected removeRange(range: ColorScaleRange) {
    this.ranges = this.ranges.filter((r: ColorScaleRange) => r !== range);
    let numRanges: number = this.ranges.length;
    if (numRanges === 0) {
      return;
    }
    this.colorScaleChanged.emit(this.dataPoint.colorScale);
  }

  protected handleRangeChanged(range: ColorScaleRange) {
    const numRanges: number = this.ranges.length;
    const lastRange: ColorScaleRange = this.ranges[numRanges - 1];
    if (!(lastRange.fromValue === null && lastRange.toValue === null)) {
      this.ranges.push(new ColorScaleRange());
      this.cdr.detectChanges();
    }

    this.colorScaleChanged.emit(this.dataPoint.colorScale);
  }

  protected clear() {
    this.ranges = [new ColorScaleRange()];
    this.colorScaleChanged.emit(this.dataPoint.colorScale);
  }

  protected apply() {
    this.closeDesired.emit();
  }

  resetRangeFormControls(): void {
    this.sortedColorScaleEntries.forEach((c: ColorScaleEntry) => c.setValuesFromModel());
  }

  protected searchDataPointsWithColorScale(event: AutoCompleteCompleteEvent) {
    let query: string | undefined = event.query;
    if (!query) {
      query = '';
    }
    this.copyFromDataPointSuggestions = this.editorModelService.editorModel.dataPointRows
      .flatMap((r) => r.dataPoints)
      .filter((dp: DataPoint) => !dp.colorScale.isEmpty())
      .filter((dp: DataPoint) => dp !== this.dataPoint)
      .filter(
        (dp: DataPoint) =>
          dp.displayName.toLowerCase().includes(query.toLowerCase()) ||
          dp.sourceDataPoint.internalName.toLowerCase().includes(query?.toLowerCase()),
      );
  }

  protected copyFromSelectedDataPoint() {
    this.dataPoint.colorScale = this.fcCopyFromDataPoint.value!.colorScale;
  }
}

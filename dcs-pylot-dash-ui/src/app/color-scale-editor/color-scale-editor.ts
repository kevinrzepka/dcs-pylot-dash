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

@Component({
  selector: 'app-color-scale-editor',
  imports: [ColorScaleEntry, Button, Tooltip],
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

  constructor(private cdr: ChangeDetectorRef) {}

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

  protected removeRange(range: ColorScaleRange, index: number, first: boolean) {
    this.ranges = this.ranges.filter((r: ColorScaleRange) => r !== range);
    let numRanges: number = this.ranges.length;
    if (numRanges === 0) {
      return;
    }

    const sortedColorScaleEntries: ColorScaleEntry[] = this.sortedColorScaleEntries;
    const thisRange: ColorScaleRange = this.ranges[index]; // not the removed one, but the one after it
    if (first) {
      sortedColorScaleEntries[0].handlePreviousRangeChanged(null);
    } else {
      const previousRange = this.ranges[index - 1];
      const previousRangeEntry = sortedColorScaleEntries[index - 1];
      if (index < numRanges - 1) {
        // we did not delete the second to last one, so there is a next one
        const thisRangeEntry: ColorScaleEntry = sortedColorScaleEntries[index];
        const nextRange: ColorScaleRange = this.ranges[index + 1];
        const nextRangeEntry: ColorScaleEntry = sortedColorScaleEntries[index + 1];
        previousRangeEntry.handleNextRangeChanged(thisRange);
        thisRangeEntry.handlePreviousRangeChanged(previousRange);
        thisRangeEntry.handleNextRangeChanged(nextRange);
        nextRangeEntry.handlePreviousRangeChanged(thisRange);
      } else {
        // we deleted the last one, so there is no next one
        // since the first one cannot be deleted, there will always be a previous one
        sortedColorScaleEntries[index - 1].handleNextRangeChanged(null);
      }
    }
    this.colorScaleChanged.emit(this.dataPoint.colorScale);
  }

  protected handleRangeChanged(
    range: ColorScaleRange,
    index: number,
    first: boolean,
    last: boolean,
  ) {
    const numRanges: number = this.ranges.length;
    const lastRange: ColorScaleRange = this.ranges[numRanges - 1];
    if (!(lastRange.valueFrom === null && lastRange.valueTo === null)) {
      this.ranges.push(new ColorScaleRange());
      this.cdr.detectChanges();
    }

    const sortedColorScaleEntries: ColorScaleEntry[] = this.sortedColorScaleEntries;
    if (!first) {
      sortedColorScaleEntries[index - 1].handleNextRangeChanged(range);
      if (index < sortedColorScaleEntries.length - 1) {
        sortedColorScaleEntries[index].handlePreviousRangeChanged(this.ranges[index - 1]);
      }
    }

    if (!last) {
      sortedColorScaleEntries[index + 1].handlePreviousRangeChanged(range);
      sortedColorScaleEntries[index].handleNextRangeChanged(this.ranges[index + 1]);
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
}

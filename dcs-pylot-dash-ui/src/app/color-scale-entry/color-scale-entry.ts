/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { IftaLabel } from 'primeng/iftalabel';
import { InputText } from 'primeng/inputtext';
import { Tooltip } from 'primeng/tooltip';
import { ColorPickerModule } from 'primeng/colorpicker';
import { ColorScaleRange } from '../editor-model';
import { KeyFilter } from 'primeng/keyfilter';
import { Message } from 'primeng/message';

@Component({
  selector: 'app-color-scale-entry',
  imports: [
    ReactiveFormsModule,
    IftaLabel,
    InputText,
    Tooltip,
    ColorPickerModule,
    KeyFilter,
    Message,
  ],
  templateUrl: './color-scale-entry.html',
  styleUrl: './color-scale-entry.css',
})
export class ColorScaleEntry implements OnInit, OnChanges {
  @Output()
  rangeChanged: EventEmitter<ColorScaleRange> = new EventEmitter<ColorScaleRange>();

  @Input()
  range!: ColorScaleRange;

  @Input()
  previousRange: ColorScaleRange | null = null;

  @Input()
  nextRange: ColorScaleRange | null = null;

  fg: FormGroup = new FormGroup({
    fcFrom: new FormControl<number | null>(null),
    fcTo: new FormControl<number | null>(null),
    fcColorHex: new FormControl<string>(ColorScaleRange.DEFAULT_COLOR.slice(1)),
    fcColor: new FormControl<string>(ColorScaleRange.DEFAULT_COLOR.slice(1)),
  });

  protected fromErrors: string[] = [];
  protected toErrors: string[] = [];

  ngOnInit(): void {
    this.fcColorHex.valueChanges.subscribe((value) => {
      this.fcColor.setValue(`#${value}`, { emitEvent: false });
    });
    this.fcColor.valueChanges.subscribe((value) => {
      this.fcColorHex.setValue(value.slice(1).toUpperCase(), { emitEvent: false });
    });

    this.setValuesFromModel();
    this.rangeChanged.emit(this.range);

    this.fg.valueChanges.subscribe((e) => {
      const valid: boolean = this.validate();
      if (valid) {
        const fromValue: number | null = this.fcFromValue;
        const toValue: number | null = this.fcToValue;
        const colorValue: string = this.fcColorValue;

        this.range.fromValue = fromValue;
        this.range.toValue = toValue;
        this.range.color = colorValue;
        this.rangeChanged.emit(this.range);
      }
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['previousRange'] || changes['nextRange'] || changes['range']) {
      this.validate();
    }
  }

  setValuesFromModel() {
    this.fcFrom.setValue(this.range.fromValue);
    this.fcTo.setValue(this.range.toValue);
    this.fcColor.setValue(this.range.color);
    this.validate();
  }

  protected validate(): boolean {
    const fromValue: number | null = this.fcFromValue;
    const toValue: number | null = this.fcToValue;

    const previousFromValue: number | null = this.previousRange?.fromValue ?? null;
    const previousToValue: number | null = this.previousRange?.toValue ?? null;
    const nextFromValue: number | null = this.nextRange?.fromValue ?? null;
    const nextToValue: number | null = this.nextRange?.toValue ?? null;
    const fromErrors: string[] = [];
    const toErrors: string[] = [];

    let noOwnValueSet: boolean = fromValue === null && toValue === null;
    if (noOwnValueSet && this.nextRange !== null) {
      fromErrors.push('Please specify either a From value or a To value.');
      toErrors.push('Please specify either a From value or a To value.');
    }

    if (fromValue !== null) {
      if (previousFromValue !== null && fromValue <= previousFromValue) {
        fromErrors.push(
          `From value ${fromValue} must be greater than previous range's From value ${previousFromValue}`,
        );
      }
      if (previousToValue !== null && fromValue < previousToValue) {
        fromErrors.push(
          `From value ${fromValue} must be greater than previous range's To value ${previousToValue}`,
        );
      }
    }
    this.fromErrors = fromErrors;
    this.fcFrom.setErrors(this.fromErrors.length ? this.fromErrors : null);

    if (toValue !== null) {
      if (previousToValue !== null && toValue <= previousToValue) {
        toErrors.push(
          `To value ${toValue} must be greater than previous range's To value ${previousToValue}`,
        );
      }
      if (nextFromValue !== null && toValue > nextFromValue) {
        toErrors.push(
          `To value ${toValue} must be less than next range's From value ${nextFromValue}`,
        );
      }
      if (nextToValue !== null && toValue > nextToValue) {
        toErrors.push(`To value ${toValue} must be less than next range's To value ${nextToValue}`);
      }
      if (fromValue !== null && fromValue > toValue) {
        fromErrors.push(
          `From value ${fromValue} must be less than or equal to To value ${toValue}`,
        );
        toErrors.push(
          `To value ${toValue} must be greater than or equal to From value ${fromValue}`,
        );
      }
      if (previousFromValue !== null && previousToValue === null && fromValue === null) {
        toErrors.push(
          `Ambiguous range: Please specify either a From value on this range, or a To value on the previous range.`,
        );
      }
    }
    this.toErrors = toErrors;
    this.fcTo.setErrors(this.toErrors.length ? this.toErrors : null);

    return this.fromErrors.length === 0 && this.toErrors.length === 0;
  }

  handleNextRangeChanged(colorScaleRange: ColorScaleRange | null) {
    this.nextRange = colorScaleRange;
    this.validate();
  }

  handlePreviousRangeChanged(colorScaleRange: ColorScaleRange | null) {
    this.previousRange = colorScaleRange;
    this.validate();
  }

  get fcFrom(): FormControl<number | null> {
    return this.fg.get('fcFrom')! as FormControl;
  }

  get fcTo(): FormControl<number | null> {
    return this.fg.get('fcTo')! as FormControl;
  }

  get fcColorHex(): FormControl<string> {
    return this.fg.get('fcColorHex')! as FormControl;
  }

  get fcColor(): FormControl<string> {
    return this.fg.get('fcColor')! as FormControl;
  }

  get fcFromValue(): number | null {
    return this.fcFrom.value ?? null;
  }

  get fcToValue(): number | null {
    return this.fcTo.value ?? null;
  }

  get fcColorValue(): string {
    return this.fcColor.value;
  }
}

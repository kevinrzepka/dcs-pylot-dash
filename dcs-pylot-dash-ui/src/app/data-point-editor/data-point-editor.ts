/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
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
  ViewChild,
} from '@angular/core';
import { Card } from 'primeng/card';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { InputText } from 'primeng/inputtext';
import { ColorScale, DataPoint, DataPointUnit, SourceDataPoint } from '../editor-model';
import { IftaLabel } from 'primeng/iftalabel';
import { Button, ButtonSeverity } from 'primeng/button';
import {
  SourceDataPointChangedEvent,
  SourceDataPointChooser,
} from '../source-data-point-chooser/source-data-point-chooser';
import { Tooltip } from 'primeng/tooltip';
import { UnitChooser } from '../unit-chooser/unit-chooser';
import { KeyFilter } from 'primeng/keyfilter';
import { Popover } from 'primeng/popover';
import { ColorScaleEditor } from '../color-scale-editor/color-scale-editor';
import { AsyncPipe } from '@angular/common';
import { ReplaySubject } from 'rxjs';

@Component({
  selector: 'app-data-point-editor',
  imports: [
    Card,
    FormsModule,
    InputText,
    IftaLabel,
    Button,
    SourceDataPointChooser,
    Tooltip,
    UnitChooser,
    ReactiveFormsModule,
    KeyFilter,
    Popover,
    ColorScaleEditor,
    AsyncPipe,
  ],
  templateUrl: './data-point-editor.html',
  styleUrl: './data-point-editor.css',
})
export class DataPointEditor implements OnInit {
  @Input()
  dataPoint!: DataPoint;

  @ViewChild(UnitChooser)
  unitChooser!: UnitChooser;

  @ViewChild('colorScaleButton')
  colorScaleButton!: Button;

  @ViewChild(ColorScaleEditor)
  colorScaleEditor!: ColorScaleEditor;

  colorScaleButtonSeverity$: ReplaySubject<ButtonSeverity> = new ReplaySubject(1);

  fcDisplayName: FormControl<string | null> = new FormControl();

  @Output()
  onDeleteDataPoint: EventEmitter<DataPoint> = new EventEmitter<DataPoint>();

  @Output()
  dataPointChanged: EventEmitter<DataPoint> = new EventEmitter<DataPoint>();

  protected displayNameRegex: RegExp = /^[\w\s.()]+$/;
  protected displayNameMaxLength: number = 50;

  constructor(private cdr: ChangeDetectorRef) {
    this.colorScaleButtonSeverity$.next('secondary');
  }

  ngOnInit(): void {
    this.fcDisplayName.setValue(this.dataPoint.displayName);
    this.fcDisplayName.valueChanges.subscribe((value: string | null) => {
      this.dataPoint.displayName = value ?? '';
      this.dataPointChanged.emit(this.dataPoint);
    });
  }

  protected deleteDataPoint() {
    this.onDeleteDataPoint.emit(this.dataPoint);
  }

  protected handleSourceDataPointChange(event: SourceDataPointChangedEvent) {
    const sourceDataPoint: SourceDataPoint | null = event.sourceDataPoint;
    if (sourceDataPoint) {
      this.dataPoint.sourceDataPoint = sourceDataPoint;
      this.dataPoint.outputUnit = sourceDataPoint.defaultUnit;
      if (this.dataPoint.displayName !== sourceDataPoint.displayName) {
        this.fcDisplayName.setValue(sourceDataPoint.displayName);
      }
      this.unitChooser.handleSourceDataPointChange(sourceDataPoint);
      this.dataPointChanged.emit(this.dataPoint);
    }
  }

  protected handleUnitChange(unit: DataPointUnit | null) {
    this.dataPointChanged.emit(this.dataPoint);
  }

  protected handleColorScaleChanged(colorScale: ColorScale) {
    if (this.colorScaleButton !== undefined) {
      this.colorScaleButtonSeverity$.next(colorScale.isEmpty() ? 'secondary' : 'info');
      this.cdr.detectChanges();
    }
    this.dataPointChanged.emit(this.dataPoint);
  }

  protected handleColorScalePopoverHidden($event: any) {
    this.colorScaleEditor.resetRangeFormControls();
  }
}

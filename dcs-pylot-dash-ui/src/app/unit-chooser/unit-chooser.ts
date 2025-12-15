/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Select } from 'primeng/select';
import { DataPoint, DataPointUnit, SourceDataPoint } from '../editor-model';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { IftaLabel } from 'primeng/iftalabel';

@Component({
  selector: 'app-unit-chooser',
  imports: [Select, ReactiveFormsModule, IftaLabel],
  templateUrl: './unit-chooser.html',
  styleUrl: './unit-chooser.css',
})
export class UnitChooser implements OnInit {
  availableUnits: DataPointUnit[] = [];

  @Output()
  onUnitChange: EventEmitter<DataPointUnit | null> = new EventEmitter<DataPointUnit | null>();

  @Input()
  dataPoint!: DataPoint;

  fcChosenUnit: FormControl<DataPointUnit | null> = new FormControl(null);

  protected lastChosenUnit: DataPointUnit | null = null;

  ngOnInit(): void {
    this.availableUnits = [...this.dataPoint.sourceDataPoint.availableUnits];
    this.fcChosenUnit.setValue(this.dataPoint.outputUnit);
    this.fcChosenUnit.valueChanges.subscribe((value: DataPointUnit | null) => {
      if (value && value !== this.lastChosenUnit) {
        this.dataPoint.setOutputUnit(value);
        this.onUnitChange.emit(value);
        this.lastChosenUnit = value;
      }
    });
  }

  handleSourceDataPointChange(sourceDataPoint: SourceDataPoint | null) {
    if (sourceDataPoint !== null) {
      this.availableUnits = [...sourceDataPoint.availableUnits];
      let selectedUnitId: string | undefined = this.fcChosenUnit.value?.unitId;
      if (
        !selectedUnitId ||
        !this.availableUnits.map((unit) => unit.unitId).includes(selectedUnitId)
      ) {
        this.fcChosenUnit.setValue(sourceDataPoint.defaultUnit);
      }
    } else {
      this.availableUnits = [];
      this.fcChosenUnit.setValue(null);
    }
  }
}

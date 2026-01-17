/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import {
  ChangeDetectorRef,
  Component,
  ElementRef,
  EventEmitter,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
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
import {
  SourceDataPointChangedEvent,
  SourceDataPointChooser,
} from '../source-data-point-chooser/source-data-point-chooser';
import { Tooltip } from 'primeng/tooltip';
import { GeneratorService } from '../generator-service';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Popover } from 'primeng/popover';
import { ClassNames } from 'primeng/classnames';
import { SampleModelService } from '../sample-model.service';
import { Dialog } from 'primeng/dialog';
import { first, ReplaySubject, startWith } from 'rxjs';
import {
  AdvancedSettingsConstraints,
  AdvancedSettingsDefaults,
  APIExportModelAdvancedSettings,
} from '../api-model';
import { IftaLabel } from 'primeng/iftalabel';
import { InputText } from 'primeng/inputtext';
import { Checkbox } from 'primeng/checkbox';
import { BackendStatusMessages } from '../backend-status-messages/backend-status-messages';

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
    Popover,
    ClassNames,
    Dialog,
    IftaLabel,
    InputText,
    Checkbox,
    BackendStatusMessages,
  ],
  templateUrl: './editor-page.html',
  styleUrl: './editor-page.css',
})
export class EditorPage implements OnInit {
  readonly NO_DATA_TOOLTIP: string = 'Add at least one data point to the dashboard.';

  /**
   * Should only be modified through {@link enableControlsDependingOnModelEmpty}, or {@link generate}
   * @protected
   */
  protected generateButtonEnabled: boolean = false;
  /**
   * Should only be modified through {@link enableControlsDependingOnModelEmpty}
   * @protected
   */
  protected generateButtonTooltip: string = this.NO_DATA_TOOLTIP;

  protected downloadButtonEnabled: boolean = false;
  protected downloadUrl: string | null = null;
  protected downloadFilename: string | null = 'dcs-pylot-dash-generated.zip';

  protected editorModel: EditorModel = new EditorModel();
  protected sampleModel: EditorModel | null = null;

  readonly maxRows: number = 10;
  readonly maxDataPointsPerRow: number = 6;

  loadSampleModelButtonEnabled: boolean = false;
  clearModelButtonEnabled: boolean = false;
  loadSampleModelDialogVisible: boolean = false;
  clearModelDialogVisible: boolean = false;

  @Output()
  onEditorModelChanged: EventEmitter<EditorModel> = new EventEmitter<EditorModel>();

  @ViewChild('downloadAfterBuildButton')
  downloadAfterBuildButton!: Button;

  @ViewChild('buildButton')
  buildButton!: Button;

  @ViewChild('loadSampleModelButton')
  loadSampleModelButton!: Button;

  @ViewChild('downloadPopover')
  downloadPopover!: Popover;

  @ViewChild('sampleModelPopover')
  sampleModelPopover!: Popover;

  @ViewChild('addDataPointRowChooser', { read: ElementRef })
  addDataPointRowChooserElementRef!: ElementRef;

  @ViewChild('addDataPointRowChooser')
  addDataPointRowChooser!: SourceDataPointChooser;

  @ViewChild('modellingPopover')
  modellingPopover!: Popover;

  @ViewChild('buildPopover')
  buildPopover!: Popover;

  @ViewChild('downloadLink')
  downloadLink!: ElementRef;

  downloadAfterBuildButtonStyleClass: string = '';

  userConsentGiven$: ReplaySubject<boolean> = new ReplaySubject(1);

  advancedSettingsDialogVisible: boolean = false;

  fcOverrideDefaults: FormControl<boolean | null> = new FormControl<boolean | null>(false);

  fgAdvancedSettings: FormGroup = new FormGroup({
    bindAddress: new FormControl<string | null>(AdvancedSettingsDefaults.LUA_BIND_ADDRESS),
    bindPort: new FormControl<number | null>(AdvancedSettingsDefaults.LUA_BIND_PORT),
    pollIntervalMs: new FormControl<number | null>(AdvancedSettingsDefaults.POLL_INTERVAL_MS),
  });

  protected advancedSettings: APIExportModelAdvancedSettings | null = null;

  constructor(
    private generatorService: GeneratorService,
    private sampleModelService: SampleModelService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.sampleModelService.sampleModel$.subscribe((next) => {
      this.sampleModel = next;
      if (!this.sampleModel.isEmpty()) {
        this.loadSampleModelButtonEnabled = true;
      }
      this.userConsentGiven$.pipe(first()).subscribe(() => this.showTutorialPopovers());
    });

    this.fcOverrideDefaults.valueChanges
      .pipe(startWith(false))
      .subscribe((value: boolean | null) => {
        if (value) {
          this.fgAdvancedSettings.enable();
        } else {
          this.fgAdvancedSettings.disable();
        }
      });
  }

  confirmLoadSampleModel() {
    this.editorModel = this.sampleModel!.copy();
    this.editorModelChanged();
    this.loadSampleModelDialogVisible = false;
  }

  confirmClearModel() {
    this.editorModel.dataPointRows = [];
    this.editorModelChanged();
    this.clearModelDialogVisible = false;
  }

  protected generate() {
    this.generateButtonEnabled = false;
    this.downloadButtonEnabled = false;
    const advancedSettings: APIExportModelAdvancedSettings | null = this.overrideAdvancedSettings
      ? this.advancedSettings
      : null;
    this.generatorService.generate(this.editorModel, advancedSettings).subscribe((blob) => {
      if (blob) {
        this.downloadUrl = window.URL.createObjectURL(blob);
        this.downloadButtonEnabled = true;
        this.downloadAfterBuildButtonStyleClass = 'display-none';
        this.downloadPopover.show(null, this.downloadLink.nativeElement);
      } else {
        this.enableControlsDependingOnModelEmpty();
      }
      this.advancedSettingsDialogVisible = false;
      this.cdr.detectChanges();
    });
    this.cdr.detectChanges();
  }

  protected removeDataPointRow(dataPointRow: DataPointRow) {
    this.editorModel.dataPointRows = this.editorModel.dataPointRows.filter(
      (row: DataPointRow) => row !== dataPointRow,
    );
    this.editorModelChanged();
  }

  protected removeDataPoint(
    dataPointRow: DataPointRow,
    dataPoint: DataPoint,
    sourceDataPointChooser: SourceDataPointChooser,
  ) {
    dataPointRow.removeDataPoint(dataPoint);
    this.enableOrDisableDataPointChooserForRow(dataPointRow, sourceDataPointChooser);
    this.editorModelChanged();
  }

  protected editorModelChanged() {
    this.enableControlsDependingOnModelEmpty();
    this.modellingPopover.hide();
    if (this.downloadUrl) {
      window.URL.revokeObjectURL(this.downloadUrl);
    }
    if (this.editorModel.dataPointRows.length >= this.maxRows) {
      this.addDataPointRowChooser.disable();
    } else {
      this.addDataPointRowChooser.enable();
    }
    this.downloadButtonEnabled = false;
    this.downloadAfterBuildButtonStyleClass = '';
    this.downloadUrl = null;
    this.onEditorModelChanged.emit(this.editorModel);
  }

  protected enableControlsDependingOnModelEmpty(): void {
    if (this.editorModel.isEmpty()) {
      this.generateButtonTooltip = this.NO_DATA_TOOLTIP;
      this.generateButtonEnabled = false;
      this.clearModelButtonEnabled = false;
    } else {
      this.generateButtonTooltip = '';
      this.generateButtonEnabled = true;
      this.clearModelButtonEnabled = true;
    }
  }

  protected dataPointDropped(event: CdkDragDrop<any, any>) {
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
    event: SourceDataPointChangedEvent,
    dataPointRow: DataPointRow | null = null,
  ) {
    const sourceDataPoint: SourceDataPoint | null = event.sourceDataPoint;
    if (sourceDataPoint) {
      const dataPoint: DataPoint = new DataPoint(sourceDataPoint.displayName, sourceDataPoint);
      if (dataPointRow !== null) {
        dataPointRow.addDataPoint(dataPoint);
      } else {
        dataPointRow = new DataPointRow();
        dataPointRow.addDataPoint(dataPoint);
        this.editorModel.dataPointRows.push(dataPointRow);
      }
      this.enableOrDisableDataPointChooserForRow(dataPointRow, event.source);
      this.cdr.detectChanges();
      this.editorModelChanged();
    }
  }

  protected enableOrDisableDataPointChooserForRow(
    dataPointRow: DataPointRow,
    sourceDataPointChooser: SourceDataPointChooser,
  ) {
    if (dataPointRow.dataPoints.length >= this.maxDataPointsPerRow) {
      sourceDataPointChooser.disable();
    } else {
      sourceDataPointChooser.enable();
    }
  }

  protected handleDataPointChanged() {
    this.editorModelChanged();
  }

  protected loadSampleModel() {
    this.sampleModelPopover.hide();
    if (this.editorModel.isEmpty()) {
      this.confirmLoadSampleModel();
    } else {
      this.loadSampleModelDialogVisible = true;
    }
  }

  updateUserConsentGiven(): void {
    this.userConsentGiven$.next(true);
  }

  protected showTutorialPopovers(): void {
    if (this.sampleModel !== null && !this.sampleModel.isEmpty()) {
      this.sampleModelPopover.show(null, this.loadSampleModelButton.el.nativeElement);
    }

    this.buildPopover.show(null, this.buildButton.el.nativeElement);
    this.modellingPopover.show(null, this.addDataPointRowChooserElementRef.nativeElement);
  }

  protected showAdvancedSettings() {
    this.advancedSettingsDialogVisible = true;
  }

  protected get overrideAdvancedSettings(): boolean {
    return this.fcOverrideDefaults.value ?? false;
  }

  protected get fcBindAddress(): FormControl<string | null> {
    return this.fgAdvancedSettings.get('bindAddress') as FormControl<string | null>;
  }

  protected get fcBindPort(): FormControl<number | null> {
    return this.fgAdvancedSettings.get('bindPort') as FormControl<number | null>;
  }

  protected get fcPollIntervalMs(): FormControl<number | null> {
    return this.fgAdvancedSettings.get('pollIntervalMs') as FormControl<number | null>;
  }

  protected readonly AdvancedSettingsConstraints = AdvancedSettingsConstraints;

  protected resetAdvancedSettings() {
    this.fcBindAddress.setValue(AdvancedSettingsDefaults.LUA_BIND_ADDRESS);
    this.fcBindPort.setValue(AdvancedSettingsDefaults.LUA_BIND_PORT);
    this.fcPollIntervalMs.setValue(AdvancedSettingsDefaults.POLL_INTERVAL_MS);
    this.fcOverrideDefaults.setValue(false);
  }

  protected saveAdvancedSettings() {
    const bindAddress: string | null = this.fcBindAddress.value;
    const bindPort: number | null = this.fcBindPort.value;
    const pollIntervalMs: number | null = this.fcPollIntervalMs.value;
    this.advancedSettings = {
      lua_bind_address: bindAddress,
      lua_bind_port: bindPort,
      poll_interval_ms: pollIntervalMs,
    };
    this.advancedSettingsDialogVisible = false;
  }
}

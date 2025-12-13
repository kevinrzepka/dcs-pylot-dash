/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { DataPointUnit, SourceDataPoint } from './editor-model';
import { ReplaySubject } from 'rxjs';
import { ApiSourceModelService } from './api-source-model-service';
import { APISourceModel, APIUnit } from './api-model';

@Injectable({
  providedIn: 'root',
})
export class SourceDataPointService {
  sourceDataPoints: ReplaySubject<SourceDataPoint[]> = new ReplaySubject(1);
  sourceDataPoints2: ReplaySubject<SourceDataPoint[]> = new ReplaySubject(1);

  constructor(private apiService: ApiSourceModelService) {
    this.loadSourceDataPoints();
    this.loadSourceDataPoints2();
  }

  loadSourceDataPoints2() {
    this.apiService.apiSourceModel.subscribe((apiModel: APISourceModel) => {
      const sourceDataPoints: SourceDataPoint[] = this.buildSourceDataPointsFromAPIModel(apiModel);
      this.sourceDataPoints2.next(sourceDataPoints);
    });
  }

  private buildSourceDataPointsFromAPIModel(apiModel: APISourceModel): SourceDataPoint[] {
    const apiUnitsById: Map<string, APIUnit> = new Map<string, APIUnit>();
    for (const apiUnit of apiModel.units) {
      apiUnitsById.set(apiUnit.unitId, apiUnit);
    }
    const sourceDataPoints: SourceDataPoint[] = [];
    for (const apiField of apiModel.fields) {
      const defaultApiUnit: APIUnit = apiUnitsById.get(apiField.defaultUnitId)!;
      const fieldDefaultUnit: DataPointUnit = this.createDataPointUnitFromAPIUnit(defaultApiUnit);
      const availableUnits: DataPointUnit[] = apiField.availableUnitIds.map((unitId: string) => {
        const apiUnit: APIUnit = apiUnitsById.get(unitId)!;
        return this.createDataPointUnitFromAPIUnit(apiUnit);
      });

      const sourceDataPoint: SourceDataPoint = new SourceDataPoint(
        apiField.displayName,
        apiField.internalName,
        fieldDefaultUnit,
        availableUnits,
      );
      sourceDataPoints.push(sourceDataPoint);
    }
    return sourceDataPoints;
  }

  private createDataPointUnitFromAPIUnit(apiUnit: APIUnit): DataPointUnit {
    return new DataPointUnit(apiUnit.displayName, apiUnit.unitId, apiUnit.symbol);
  }

  loadSourceDataPoints() {
    const units = [
      new DataPointUnit('m/s', 'tas_ms', 'm/s'),
      new DataPointUnit('kts', 'knots', 'kts'),
    ];
    const sourceDataPoints = [
      new SourceDataPoint('TAS kts', 'tas', units[1], units),
      new SourceDataPoint('TAS ms', 'tas', units[0], units),
    ];
    this.sourceDataPoints.next(sourceDataPoints);
  }
}

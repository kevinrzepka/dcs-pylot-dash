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

  constructor(private apiService: ApiSourceModelService) {
    this.loadSourceDataPoints();
  }

  loadSourceDataPoints() {
    this.apiService.apiSourceModel.subscribe((apiModel: APISourceModel) => {
      const sourceDataPoints: SourceDataPoint[] = this.buildSourceDataPointsFromAPIModel(apiModel);
      this.sourceDataPoints.next(sourceDataPoints);
    });
  }

  private buildSourceDataPointsFromAPIModel(apiModel: APISourceModel): SourceDataPoint[] {
    const apiUnitsById: Map<string, APIUnit> = new Map<string, APIUnit>();
    for (const apiUnit of apiModel.units) {
      apiUnitsById.set(apiUnit.unit_id, apiUnit);
    }
    const sourceDataPoints: SourceDataPoint[] = [];
    for (const apiField of apiModel.fields) {
      const defaultApiUnit: APIUnit = apiUnitsById.get(apiField.default_unit_id)!;
      const fieldDefaultUnit: DataPointUnit = this.createDataPointUnitFromAPIUnit(defaultApiUnit);
      const availableUnits: DataPointUnit[] = apiField.available_unit_ids.map((unitId: string) => {
        const apiUnit: APIUnit = apiUnitsById.get(unitId)!;
        return this.createDataPointUnitFromAPIUnit(apiUnit);
      });

      const sourceDataPoint: SourceDataPoint = new SourceDataPoint(
        apiField.display_name,
        apiField.field_id,
        fieldDefaultUnit,
        availableUnits,
      );
      sourceDataPoints.push(sourceDataPoint);
    }
    return sourceDataPoints;
  }

  private createDataPointUnitFromAPIUnit(apiUnit: APIUnit): DataPointUnit {
    return new DataPointUnit(apiUnit.display_name, apiUnit.unit_id, apiUnit.symbol);
  }
}

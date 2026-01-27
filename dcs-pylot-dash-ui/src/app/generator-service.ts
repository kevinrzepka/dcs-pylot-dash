/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import {
  DataPoint,
  DataPointRow,
  DataPointUnit,
  EditorModel,
  SourceDataPoint,
} from './editor-model';
import {
  APIExportField,
  APIExportModel,
  APIExportModelAdvancedSettings,
  APIExportRow,
} from './api-model';
import { ApiRoutes } from './api-routes';
import { catchError, map, Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GeneratorService {
  constructor(private httpClient: HttpClient) {}

  public generate(
    editorModel: EditorModel,
    advancedSettings: APIExportModelAdvancedSettings | null,
  ): Observable<Blob | null> {
    const apiExportModel: APIExportModel = this.buildAPIExportModel(editorModel, advancedSettings);
    return this.httpClient
      .post(ApiRoutes.GENERATE, apiExportModel, {
        responseType: 'blob',
        observe: 'response',
      })
      .pipe(
        map((response: HttpResponse<Blob>) => response.body),
        catchError((err, caught) => of(null)),
      );
  }

  protected buildAPIExportModel(
    editorModel: EditorModel,
    advancedSettings: APIExportModelAdvancedSettings | null,
  ): APIExportModel {
    const apiExportModel: APIExportModel = {
      rows: [],
      advanced_settings: advancedSettings,
    };
    for (const row of editorModel.dataPointRows) {
      const apiRow: APIExportRow = {
        fields: [],
      };
      apiExportModel.rows.push(apiRow);
      for (const field of row.dataPoints) {
        const apiField: APIExportField = {
          display_name: field.displayName,
          field_id: field.sourceDataPoint.internalName,
          unit_id: field.outputUnit.unitId,
        };
        apiRow.fields.push(apiField);
      }
    }
    return apiExportModel;
  }

  buildEditorModel(
    apiExportModel: APIExportModel,
    sourceDataPoints: Map<string, SourceDataPoint>,
  ): EditorModel {
    const editorModel: EditorModel = new EditorModel();
    for (const apiRow of apiExportModel.rows) {
      const dataPointRow: DataPointRow = new DataPointRow();
      for (const apiField of apiRow.fields) {
        const sourceDataPoint: SourceDataPoint | undefined = sourceDataPoints.get(
          apiField.field_id,
        );
        const dataPointUnit: DataPointUnit | undefined = sourceDataPoint?.availableUnits.find(
          (u) => u.unitId === apiField.unit_id,
        );
        if (sourceDataPoint !== undefined && dataPointUnit !== undefined) {
          const dataPoint: DataPoint = new DataPoint(
            apiField.display_name,
            sourceDataPoint,
            dataPointUnit,
          );
          dataPointRow.addDataPoint(dataPoint);
        }
      }
      if (!dataPointRow.isEmpty()) {
        editorModel.dataPointRows.push(dataPointRow);
      }
    }
    return editorModel;
  }
}

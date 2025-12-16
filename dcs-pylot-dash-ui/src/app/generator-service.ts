/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { EditorModel } from './editor-model';
import { APIExportField, APIExportModel, APIExportRow } from './api-model';
import { ApiRoutes } from './api-routes';
import { map, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GeneratorService {
  constructor(private httpClient: HttpClient) {}

  public generate(editorModel: EditorModel): Observable<Blob | null> {
    const apiExportModel: APIExportModel = this.buildAPIExportModel(editorModel);
    return this.httpClient
      .post(ApiRoutes.GENERATE, apiExportModel, {
        responseType: 'blob',
        observe: 'response',
      })
      .pipe(map((response: HttpResponse<Blob>) => response.body));
  }

  protected buildAPIExportModel(editorModel: EditorModel): APIExportModel {
    const apiExportModel: APIExportModel = {
      rows: [],
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
}

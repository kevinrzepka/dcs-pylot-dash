/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { first, forkJoin, map, Observable, ReplaySubject } from 'rxjs';
import { APIExportModel } from './api-model';
import { HttpClient } from '@angular/common/http';
import { SourceDataPointService } from './source-data-point-service';
import { GeneratorService } from './generator-service';
import { EditorModel, SourceDataPoint } from './editor-model';
import { ApiRoutes } from './api-routes';

@Injectable({
  providedIn: 'root',
})
export class SampleModelService {
  sampleModel$: ReplaySubject<EditorModel> = new ReplaySubject(1);

  constructor(
    private httpClient: HttpClient,
    private sourceDataPointService: SourceDataPointService,
    private generatorService: GeneratorService,
  ) {
    this.loadSampleModel();
  }

  private loadSampleModel() {
    const sourceDataPointsMap$: Observable<Map<string, SourceDataPoint>> =
      this.sourceDataPointService.sourceDataPoints.pipe(
        first(),
        map(
          (a: SourceDataPoint[]) =>
            new Map<string, SourceDataPoint>(a.map((dp: SourceDataPoint) => [dp.internalName, dp])),
        ),
      );
    const sampleModel$ = this.httpClient.get<APIExportModel>(ApiRoutes.SAMPLE_MODEL);
    forkJoin({ sdpMap: sourceDataPointsMap$, sampleModel: sampleModel$ })
      .pipe(
        map((forked) => this.generatorService.buildEditorModel(forked.sampleModel, forked.sdpMap)),
      )
      .subscribe((next: EditorModel) => this.sampleModel$.next(next));
  }
}

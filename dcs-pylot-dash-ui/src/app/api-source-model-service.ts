/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { APISourceModel } from './api-model';
import { catchError, filter, Observable, of, ReplaySubject } from 'rxjs';
import { ApiRoutes } from './api-routes';
import { StatusMessageService } from './status-message-service';

@Injectable({
  providedIn: 'root',
})
export class ApiSourceModelService {
  private apiSourceModel$: ReplaySubject<APISourceModel> = new ReplaySubject(1);

  constructor(
    private httpClient: HttpClient,
    private statusMessageService: StatusMessageService,
  ) {
    this.loadAPISourceModel();
  }

  loadAPISourceModel() {
    this.httpClient
      .get<APISourceModel>(ApiRoutes.SOURCE_MODEL)
      .pipe(
        catchError((error: any, caught: Observable<APISourceModel>) => {
          this.statusMessageService.addGenericAPIErrorMessage();
          return of(null);
        }),
        filter((next: APISourceModel | null) => next !== null),
      )
      .subscribe((next: APISourceModel) => this.apiSourceModel$.next(next));
  }

  get apiSourceModel(): Observable<APISourceModel> {
    return this.apiSourceModel$;
  }
}

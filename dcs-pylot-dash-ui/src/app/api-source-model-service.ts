/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { APISourceModel } from './api-model';
import { Observable, ReplaySubject } from 'rxjs';
import { ApiRoutes } from './api-routes';

@Injectable({
  providedIn: 'root',
})
export class ApiSourceModelService {
  private apiSourceModel$: ReplaySubject<APISourceModel> = new ReplaySubject(1);

  constructor(private httpClient: HttpClient) {
    this.loadAPISourceModel();
  }

  loadAPISourceModel() {
    this.httpClient
      .get<APISourceModel>(ApiRoutes.SOURCE_MODEL)
      .subscribe((next: APISourceModel) => this.apiSourceModel$.next(next));
  }

  get apiSourceModel(): Observable<APISourceModel> {
    return this.apiSourceModel$;
  }
}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ReplaySubject } from 'rxjs';
import { APIAppMetadata } from './api-model';
import { ApiRoutes } from './api-routes';

export class AppMetadata {
  version: string;
  buildDate: string;
  buildCommit: string;

  constructor(version: string, buildDate: string, buildCommit: string) {
    this.version = version;
    this.buildDate = buildDate;
    this.buildCommit = buildCommit;
  }
}

@Injectable({
  providedIn: 'root',
})
export class AppMetadataService {
  appMetadata: ReplaySubject<AppMetadata> = new ReplaySubject(1);

  constructor(private httpClient: HttpClient) {
    this.loadAppMetadata();
  }

  protected loadAppMetadata() {
    this.httpClient.get<APIAppMetadata>(ApiRoutes.METADATA).subscribe((next: APIAppMetadata) => {
      this.appMetadata.next(new AppMetadata(next.version, next.build_date, next.build_commit));
    });
  }
}

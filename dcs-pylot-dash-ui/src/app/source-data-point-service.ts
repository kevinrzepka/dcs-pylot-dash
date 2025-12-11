/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { DataPointUnit, SourceDataPoint } from './editor-model';
import { ReplaySubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class SourceDataPointService {
  sourceDataPoints: ReplaySubject<SourceDataPoint[]> = new ReplaySubject(1);

  constructor() {
    this.loadSourceDataPoints();
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

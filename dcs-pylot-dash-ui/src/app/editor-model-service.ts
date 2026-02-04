/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { EditorModel } from './editor-model';
import { SampleModelService } from './sample-model.service';
import { ReplaySubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class EditorModelService {
  editorModel: EditorModel = new EditorModel();
  sampleModel$: ReplaySubject<EditorModel> = new ReplaySubject(1);

  constructor(private sampleModelService: SampleModelService) {
    this.sampleModelService.sampleModel$.subscribe((next) => {
      this.sampleModel$.next(next);
    });
  }

  loadSampleModel() {
    this.sampleModel$.subscribe((next) => {
      this.editorModel = next.copy();
    });
  }
}

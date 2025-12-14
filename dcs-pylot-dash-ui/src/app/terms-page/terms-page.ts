/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, Signal } from '@angular/core';
import { NoticesService } from '../notices-service';
import { toSignal } from '@angular/core/rxjs-interop';
import { Card } from 'primeng/card';

@Component({
  selector: 'app-terms-page',
  imports: [Card],
  templateUrl: './terms-page.html',
  styleUrl: './terms-page.css',
})
export class TermsPage {
  termsOfServiceContent: Signal<string>;

  constructor(private noticesService: NoticesService) {
    this.termsOfServiceContent = toSignal(this.noticesService.termsOfServiceHtml, {
      initialValue: '',
    });
  }
}

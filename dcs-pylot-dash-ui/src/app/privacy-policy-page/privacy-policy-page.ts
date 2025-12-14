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
  selector: 'app-privacy-policy-page',
  imports: [Card],
  templateUrl: './privacy-policy-page.html',
  styleUrl: './privacy-policy-page.css',
})
export class PrivacyPolicyPage {
  privacyPolicyContent: Signal<string>;

  constructor(private noticesService: NoticesService) {
    this.privacyPolicyContent = toSignal(this.noticesService.privacyPolicyHtml, {
      initialValue: '',
    });
  }
}

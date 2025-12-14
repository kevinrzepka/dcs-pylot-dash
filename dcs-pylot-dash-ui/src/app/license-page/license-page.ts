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
  selector: 'app-license-page',
  imports: [Card],
  templateUrl: './license-page.html',
  styleUrl: './license-page.css',
})
export class LicensePage {
  licenseContent: Signal<string>;

  constructor(private noticesService: NoticesService) {
    this.licenseContent = toSignal(this.noticesService.licenseTxt, { initialValue: '' });
  }
}

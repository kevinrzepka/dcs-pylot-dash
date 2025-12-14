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
  selector: 'app-third-party-licenses-page',
  imports: [Card],
  templateUrl: './third-party-licenses-page.html',
  styleUrl: './third-party-licenses-page.css',
})
export class ThirdPartyLicensesPage {
  thirdPartyLicensesContent: Signal<string>;

  constructor(private noticesService: NoticesService) {
    this.thirdPartyLicensesContent = toSignal(this.noticesService.thirdPartyLicensesTxt, {
      initialValue: '',
    });
  }
}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { AfterViewInit, Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Dialog } from 'primeng/dialog';
import { Button, ButtonDirective, ButtonLabel } from 'primeng/button';
import { UserDataService } from '../user-data-service';
import { AppRoutes } from '../app.routes';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-entry-consent',
  imports: [Dialog, Button, ButtonDirective, ButtonLabel, RouterLink],
  templateUrl: './entry-consent.html',
  styleUrl: './entry-consent.css',
})
export class EntryConsent implements OnInit, AfterViewInit {
  protected appRoutes = AppRoutes;

  protected dialogVisible: boolean = true;

  public readonly consentHeader: string = 'We value your privacy!';
  public readonly consentText: string =
    'This non-commercial website only uses cookies or similar technologies that are strictly necessary for its proper operation. \nWe do not employ any third-party tracking or analytics services. There are no ads.';
  public readonly disclaimerText: string =
    'This non-commercial project is not affiliated with, associated with, authorized by, endorsed by, approved by, or in any other way officially connected with "DCS World", "Eagle Dynamics SA" and/or any of its subsidiaries, affiliates, and related entities. \nThe official website of "DCS World" can be found at https://www.digitalcombatsimulator.com/';

  @Output()
  onConsentGiven: EventEmitter<void> = new EventEmitter<void>();

  constructor(private userDataService: UserDataService) {}
  ngAfterViewInit(): void {
    const consentGiven: boolean = this.userDataService.isUserConsentGiven();
    if (consentGiven) {
      this.onConsentGiven.emit();
    }
  }

  ngOnInit(): void {
    const consentGiven: boolean = this.userDataService.isUserConsentGiven();
    this.dialogVisible = !consentGiven;
  }

  protected consent() {
    this.userDataService.storeUserConsent();
    this.dialogVisible = !this.userDataService.isUserConsentGiven();
    this.onConsentGiven.emit();
  }
}

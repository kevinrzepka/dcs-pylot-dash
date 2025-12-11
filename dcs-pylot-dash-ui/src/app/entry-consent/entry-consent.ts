/**
* Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
* SPDX-License-Identifier: MIT
* License-Filename: LICENSE
*/
import {Component} from '@angular/core';
import {Dialog} from 'primeng/dialog';
import {Button, ButtonDirective, ButtonLabel} from 'primeng/button';

@Component({
  selector: 'app-entry-consent',
  imports: [
    Dialog,
    Button,
    ButtonDirective,
    ButtonLabel
  ],
  templateUrl: './entry-consent.html',
  styleUrl: './entry-consent.css',
})
export class EntryConsent {

  protected dialogVisible: boolean = true;

  public consentHeader: string = "We value your privacy!";
  public consentText: string = "This non-commercial website only uses cookies or similar technologies that are strictly necessary for its proper operation. \nWe do not employ any third-party tracking or analytics services. There are no ads.";
  public disclaimerText: string = "This non-commercial project is not affiliated with, associated with, authorized by, endorsed by, approved by, or in any other way officially connected with \"DCS World\", \"Eagle Dynamics SA\" and/or any of its subsidiaries, affiliates, and related entities. \nThe official website of \"DCS World\" can be found at https://www.digitalcombatsimulator.com/"

  protected consent() {
    this.dialogVisible = false;
  }

  protected reject() {

  }
}

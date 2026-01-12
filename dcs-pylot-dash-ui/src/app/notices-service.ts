/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { ReplaySubject } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { ApiRoutes } from './api-routes';
import { APINotices } from './api-model';

import DOMPurify from 'dompurify';
import { marked } from 'marked';

@Injectable({
  providedIn: 'root',
})
export class NoticesService {
  licenseTxt: ReplaySubject<string> = new ReplaySubject(1);
  thirdPartyLicensesTxt: ReplaySubject<string> = new ReplaySubject(1);
  termsOfServiceHtml: ReplaySubject<string> = new ReplaySubject(1);
  privacyPolicyHtml: ReplaySubject<string> = new ReplaySubject(1);

  constructor(private httpClient: HttpClient) {
    this.loadNotices();
  }

  private loadNotices() {
    this.httpClient.get<APINotices>(ApiRoutes.NOTICES).subscribe((next: APINotices) => {
      this.thirdPartyLicensesTxt.next(next.third_party_licenses_txt);
      this.licenseTxt.next(next.license_txt);
      this.termsOfServiceHtml.next(this.markdownToHtml(next.terms_of_service_md));
      this.privacyPolicyHtml.next(this.markdownToHtml(next.privacy_policy_md));
    });
  }

  private markdownToHtml(markdown: string): string {
    const parsed: string = marked.parse(markdown) as string;
    return DOMPurify.sanitize(parsed, { RETURN_TRUSTED_TYPE: true }) as unknown as string;
  }
}

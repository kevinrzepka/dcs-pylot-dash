/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Routes } from '@angular/router';
import { LicensePage } from './license-page/license-page';
import { MainPage } from './main-page/main-page';
import { PrivacyPolicyPage } from './privacy-policy-page/privacy-policy-page';
import { TermsPage } from './terms-page/terms-page';
import { ThirdPartyLicensesPage } from './third-party-licenses-page/third-party-licenses-page';

export class AppRoutes {
  static readonly LICENSE: string = 'license';
  static readonly PRIVACY_POLICY: string = 'privacy';
  static readonly TERMS_OF_SERVICE: string = 'terms-of-service';
  static readonly THIRD_PARTY_LICENSES: string = 'third-party-licenses';
}

export const routes: Routes = [
  { path: '', component: MainPage },
  { path: AppRoutes.LICENSE, component: LicensePage },
  { path: AppRoutes.PRIVACY_POLICY, component: PrivacyPolicyPage },
  { path: AppRoutes.TERMS_OF_SERVICE, component: TermsPage },
  { path: AppRoutes.THIRD_PARTY_LICENSES, component: ThirdPartyLicensesPage },
];

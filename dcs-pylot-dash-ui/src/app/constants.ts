/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
export class AppConstants {
  static readonly APP_NAME: string = 'DCS Pylot Dash Builder';

  static readonly GITHUB_BASE_URL: string = 'https://github.com/kevinrzepka/dcs-pylot-dash';
  static readonly GITHUB_ISSUES_URL: string = `${AppConstants.GITHUB_BASE_URL}/issues`;
  static readonly GITHUB_NEW_ISSUE_URL: string = `${AppConstants.GITHUB_ISSUES_URL}/new`;
  static readonly GITHUB_SECURITY_POLICY_URL: string = `${AppConstants.GITHUB_BASE_URL}/security/policy`;
  static readonly GITHUB_REPORT_SECURITY_ISSUE_URL: string = `${AppConstants.GITHUB_BASE_URL}/security/advisories/new`;
}

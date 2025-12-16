/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
export class ApiRoutes {
  static readonly BASE: string = '/api/v1';
  static readonly SOURCE_MODEL: string = `${ApiRoutes.BASE}/source-model`;
  static readonly NOTICES: string = `${ApiRoutes.BASE}/notices`;
  static readonly METADATA: string = `${ApiRoutes.BASE}/metadata`;
}

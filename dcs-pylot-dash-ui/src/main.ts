/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import DOMPurify from 'dompurify';

if (window.trustedTypes && window.trustedTypes.createPolicy) {
  window.trustedTypes.createPolicy('default', {
    createHTML: (string: any) =>
      DOMPurify.sanitize(string, { RETURN_TRUSTED_TYPE: false }) as string,
  });
}

bootstrapApplication(App, appConfig).catch((err) => console.error(err));

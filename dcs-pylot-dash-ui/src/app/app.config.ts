/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { providePrimeNG } from 'primeng/config';
import Lara from '@primeuix/themes/lara';
import Nora from '@primeuix/themes/nora';
import Aura from '@primeuix/themes/aura';
import Material from '@primeuix/themes/material';

const themeAura = {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
};

const themeMaterial = {
  theme: {
    preset: Material,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
};

const themeLara = {
  theme: {
    preset: Lara,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
};

const themeNora = {
  theme: {
    preset: Nora,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    providePrimeNG(themeAura),
  ],
};

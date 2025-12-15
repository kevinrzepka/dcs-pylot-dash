/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { EntryConsent } from './entry-consent/entry-consent';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, EntryConsent],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('dcs-pylot-dash-ui');
}

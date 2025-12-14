/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Toolbar } from 'primeng/toolbar';
import { RouterLink } from '@angular/router';
import { AppRoutes } from '../app.routes';
import { Card } from 'primeng/card';

@Component({
  selector: 'app-footer-toolbar',
  imports: [Toolbar, RouterLink, Card],
  templateUrl: './footer-toolbar.html',
  styleUrl: './footer-toolbar.css',
})
export class FooterToolbar {
  protected appRoutes = AppRoutes;
}

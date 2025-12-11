/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Toolbar } from 'primeng/toolbar';
import { Button } from 'primeng/button';

@Component({
  selector: 'app-footer-toolbar',
  imports: [Toolbar, Button],
  templateUrl: './footer-toolbar.html',
  styleUrl: './footer-toolbar.css',
})
export class FooterToolbar {}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { Button } from 'primeng/button';

@Component({
  selector: 'app-hello',
  imports: [Button],
  templateUrl: './hello.html',
  styleUrl: './hello.css',
})
export class Hello {}

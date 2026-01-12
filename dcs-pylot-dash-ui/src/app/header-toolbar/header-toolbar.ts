/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, Input } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Toolbar } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MenuSidebar } from '../menu-sidebar/menu-sidebar';
import { AppConstants } from '../constants';

@Component({
  selector: 'app-header-toolbar',
  imports: [Toolbar, ButtonModule, InputTextModule],
  templateUrl: './header-toolbar.html',
  styleUrl: './header-toolbar.css',
})
export class HeaderToolbar {
  items: MenuItem[] | undefined;
  @Input() menuSidebar!: MenuSidebar;

  protected toggleSidebar() {
    this.menuSidebar.visible = !this.menuSidebar.visible;
  }

  protected readonly AppConstants = AppConstants;
}

/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component, OnInit } from '@angular/core';
import { Drawer } from 'primeng/drawer';
import { AppRoutes } from '../app.routes';
import { Menu } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { AppConstants } from '../constants';

@Component({
  selector: 'app-menu-sidebar',
  imports: [Drawer, Menu],
  templateUrl: './menu-sidebar.html',
  styleUrl: './menu-sidebar.css',
})
export class MenuSidebar implements OnInit {
  public visible: boolean = false;

  menuItems: MenuItem[] = [];

  ngOnInit() {
    this.menuItems = [
      { label: 'FAQ', icon: 'pi pi-question', routerLink: AppRoutes.FAQ, target: '_blank' },
    ];
  }

  protected readonly AppConstants = AppConstants;
}

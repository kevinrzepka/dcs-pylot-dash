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
      {
        label: 'Bugs',
        icon: 'pi pi-list',
        url: AppConstants.GITHUB_ISSUES_URL,
        target: '_blank',
      },
      {
        label: 'Report a Bug',
        icon: 'pi pi-flag',
        url: AppConstants.GITHUB_NEW_ISSUE_URL,
        target: '_blank',
      },
      {
        label: 'Security Policy',
        icon: 'pi pi-building-columns',
        url: AppConstants.GITHUB_SECURITY_POLICY_URL,
        target: '_blank',
      },
      {
        label: 'Report a Security Issue',
        icon: 'pi pi-shield',
        url: AppConstants.GITHUB_REPORT_SECURITY_ISSUE_URL,
        target: '_blank',
      },
    ];
  }
}

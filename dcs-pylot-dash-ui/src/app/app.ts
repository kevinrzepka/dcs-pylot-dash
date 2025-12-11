/**
* Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
* SPDX-License-Identifier: MIT
* License-Filename: LICENSE
*/
import {Component, signal} from '@angular/core';
import {Hello} from './hello/hello';
import {HeaderToolbar} from './header-toolbar/header-toolbar';
import {MenuSidebar} from './menu-sidebar/menu-sidebar';
import {FooterToolbar} from './footer-toolbar/footer-toolbar';

@Component({
  selector: 'app-root',
  imports: [Hello, HeaderToolbar, MenuSidebar, FooterToolbar],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('dcs-pylot-dash-ui');
}

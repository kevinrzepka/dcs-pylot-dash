/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Component } from '@angular/core';
import { EditorPage } from '../editor-page/editor-page';
import { FooterToolbar } from '../footer-toolbar/footer-toolbar';
import { HeaderToolbar } from '../header-toolbar/header-toolbar';
import { MenuSidebar } from '../menu-sidebar/menu-sidebar';

@Component({
  selector: 'app-main-page',
  imports: [EditorPage, FooterToolbar, HeaderToolbar, MenuSidebar],
  templateUrl: './main-page.html',
  styleUrl: './main-page.css',
})
export class MainPage {}

/**
* Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
* SPDX-License-Identifier: MIT
* License-Filename: LICENSE
*/
import {Component} from '@angular/core';
import {Drawer} from 'primeng/drawer';

@Component({
  selector: 'app-menu-sidebar',
  imports: [
    Drawer
  ],
  templateUrl: './menu-sidebar.html',
  styleUrl: './menu-sidebar.css',
})
export class MenuSidebar {
  public visible: boolean = false;

}

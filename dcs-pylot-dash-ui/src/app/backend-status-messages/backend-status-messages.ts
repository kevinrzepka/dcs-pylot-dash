/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Message } from 'primeng/message';
import { StatusMessageService } from '../status-message-service';

@Component({
  selector: 'app-backend-status-messages',
  imports: [Message],
  templateUrl: './backend-status-messages.html',
  styleUrl: './backend-status-messages.css',
})
export class BackendStatusMessages implements OnInit {
  errorMessages: string[] = [];

  constructor(
    private statusMessageService: StatusMessageService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.statusMessageService.messages$.subscribe((messages) => {
      this.errorMessages = messages.map((m) => m.content);
      this.cdr.detectChanges();
    });
  }
}

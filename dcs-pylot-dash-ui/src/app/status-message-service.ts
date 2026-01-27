/**
 * Copyright (c) 2026 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { ReplaySubject } from 'rxjs';
import { AppConstants } from './constants';

export interface StatusMessage {
  severity: string;
  content: string;
}

@Injectable({
  providedIn: 'root',
})
export class StatusMessageService {
  readonly API_ERROR_TEXT: string = `An error occurred while communicating with the API. Please try again later by force-reloading this page by pressing CTRL+R. If this error persists, please submit a bug report at ${AppConstants.GITHUB_NEW_ISSUE_URL}`;

  messages$: ReplaySubject<StatusMessage[]> = new ReplaySubject(1);
  messages: StatusMessage[] = [];

  addMessage(message: StatusMessage) {
    this.messages.push(message);
    this.messages$.next(this.messages);
  }

  removeMessage(message: StatusMessage) {
    this.messages = this.messages.filter((m: StatusMessage) => m !== message);
    this.messages$.next(this.messages);
  }

  addErrorMessage(messageContent: string) {
    const message: StatusMessage = { severity: 'error', content: messageContent };
    this.addMessage(message);
  }

  addGenericAPIErrorMessage() {
    this.addErrorMessage(this.API_ERROR_TEXT);
  }
}

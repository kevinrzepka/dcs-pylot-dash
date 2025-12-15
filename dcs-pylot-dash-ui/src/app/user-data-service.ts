/**
 * Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
 * SPDX-License-Identifier: MIT
 * License-Filename: LICENSE
 */
import { Injectable } from '@angular/core';
import { LocalStorageService } from './local-storage-service';

export type UserConsent = {
  version: string;
  accepted: boolean;
};

export type UserData = {
  consent: UserConsent;
};

@Injectable({
  providedIn: 'root',
})
export class UserDataService {
  static readonly USER_DATA_KEY: string = 'user-data';

  constructor(private localStorageService: LocalStorageService) {}

  public isUserConsentGiven(): boolean {
    const userData: UserData | null = this.loadUserData();
    if (userData !== null) {
      return userData.consent.accepted;
    }
    return false;
  }

  public storeUserConsent() {
    let userData: UserData | null = this.loadUserData();
    if (userData === null) {
      userData = { consent: { version: '1.0', accepted: true } };
    }
    userData.consent.accepted = true;
    this.localStorageService.setItem(UserDataService.USER_DATA_KEY, JSON.stringify(userData));
  }

  loadUserData(): UserData | null {
    let userDataString: string | null = this.localStorageService.getItem('user-data');
    if (userDataString !== null) {
      try {
        const userDataObject = JSON.parse(userDataString) as UserData;
        if (userDataObject.consent && userDataObject.consent.version) {
          return userDataObject;
        }
      } catch (e) {
        // clear corrupted data
        this.localStorageService.removeItem(UserDataService.USER_DATA_KEY);
      }
    }
    return null;
  }
}

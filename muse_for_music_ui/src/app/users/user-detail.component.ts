
import {timer as observableTimer,  Observable, Subject, } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, ViewChild } from '@angular/core';

import { UserApiService } from '../shared/rest/user-api.service';
import { myDialogComponent } from '../shared/dialog/dialog.component';

@Component({
  selector: 'm4m-user-detail',
  templateUrl: './user-detail.component.html',
})
export class UserDetailComponent {

    oldPassword: string = '';

    password: string = '';
    passwordRepeat: string = '';

    passwordChangeSuccess: boolean = false;

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;

    get username() {
        return this.userApi.username;
    }

    constructor(private userApi: UserApiService) { }

    changePassword = () => {
        if (this.userApi.tokenIsFresh) {
            this.userApi.changePassword(this.password, this.passwordRepeat).pipe(take(1)).subscribe(_ => {
                this.passwordChangeSuccess = true;
                observableTimer(2000).pipe(take(1)).subscribe(() => this.passwordChangeSuccess = undefined);
            });
            this.password = '';
            this.passwordRepeat = '';
        } else {
            if (this.oldPassword != null && this.oldPassword.length > 1) {
                this.oldPassword = '';
                this.userApi.freshLogin(this.oldPassword).pipe(take(1)).subscribe(success => {
                    this.changePassword();
                });
            } else {
                this.loginDialog.open();
            }
        }
    }

    hasRole(role: string): boolean {
        return this.userApi.roles.has(role);
    }

    refreshLogin() {
        this.userApi.refreshLogin(this.userApi.refreshToken);
    }
}

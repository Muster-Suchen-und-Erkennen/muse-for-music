
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

    @ViewChild('renewLoginDialog', {static: false}) loginDialog: myDialogComponent;

    constructor(private userApi: UserApiService) { }

    changePassword = () => {
        if (this.userApi.tokenIsFresh) {
            this.userApi.changePassword(this.password, this.passwordRepeat).subscribe(_ => {
                this.passwordChangeSuccess = true;
                observableTimer(2000).pipe(take(1)).subscribe(() => this.passwordChangeSuccess = undefined);
            });
            this.password = '';
            this.passwordRepeat = '';
        } else {
            if (this.oldPassword != null && this.oldPassword.length > 1) {
                this.oldPassword = '';
                this.userApi.freshLogin(this.oldPassword).subscribe(success => {
                    this.changePassword();
                });
            } else {
                this.loginDialog.open();
            }
        }
  }
}

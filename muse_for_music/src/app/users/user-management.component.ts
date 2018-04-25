import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';

import { UserApiService } from '../shared/rest/user-api.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription, Subject } from 'rxjs/Rx';
import { ApiObject } from '../shared/rest/api-base.service';
import { myDialogComponent } from '../shared/dialog/dialog.component';

@Component({
  selector: 'm4m-user-management',
  templateUrl: './user-management.component.html',
})
export class UserManagementComponent implements OnInit, OnDestroy {

    private usersubscription: Subscription;

    private freshLogin: Subject<boolean> = new Subject<boolean>();
    private pendingActionSubscription: Subscription;

    users: ApiObject[];

    private password;

    private newUsername;
    private newPassword;

    currentUser: ApiObject;
    role: string;

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;


    constructor(private navigation: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.navigation.changeTitle('MUSE4Music – Usermanagement');
        this.navigation.changeBreadcrumbs([new Breadcrumb('User', '/users')]);
        this.usersubscription = this.userApi.getUsers().subscribe(users => {
            this.users = users;
        });
    }

    ngOnDestroy(): void {
        if (this.usersubscription != null) {
            this.usersubscription.unsubscribe();
        }
    }

    addUser = () => {
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.addUser(this.newUsername, this.newPassword);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.addUser(this.newUsername, this.newPassword);
                }
            })
        }
    }

    addRole = () => {
        const user = this.currentUser;
        const role = {role: this.role};
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.addRole(user, role);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.addRole(user, role);
                }
            })
        }
    }

    removeRole = (user, role) => {
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.removeRole(user, role);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.removeRole(user, role);
                }
            })
        }
    }

    renewLogin = () => {
        if (this.userApi.tokenIsFresh) {
            this.freshLogin.next(true);
        } else {
            this.userApi.freshLogin(this.password).subscribe(success => {
                this.freshLogin.next(true);
            });
        }
    }
}

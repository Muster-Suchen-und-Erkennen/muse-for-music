import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';

import { UserApiService } from '../shared/rest/user-api.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription, Subject } from 'rxjs';
import { ApiObject } from '../shared/rest/api-base.service';
import { myDialogComponent } from '../shared/dialog/dialog.component';
import { take } from 'rxjs/operators';

@Component({
  selector: 'm4m-user-management',
  templateUrl: './user-management.component.html',
})
export class UserManagementComponent implements OnInit, OnDestroy {

    private usersubscription: Subscription;

    private freshLogin: Subject<boolean> = new Subject<boolean>();
    private pendingActionSubscription: Subscription;

    users: ApiObject[];

    password;

    newUsername;
    newPassword;
    newUserPassword;

    currentUser: ApiObject;
    role: string;

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;

    get username() {
        return this.userApi.username;
    }


    constructor(private navigation: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.navigation.changeTitle('Benutzerverwaltung');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Benutzerverwaltung', '/users')]);
        this.usersubscription = this.userApi.getUsers().subscribe(users => {
            this.users = users;
        });
    }

    ngOnDestroy(): void {
        if (this.usersubscription != null) {
            this.usersubscription.unsubscribe();
        }
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        this.freshLogin.complete();
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

    lockUser = () => {
        const currentUser = this.currentUser;
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.deleteUser(currentUser);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.deleteUser(currentUser);
                }
            })
        }
    }

    deleteUser = () => {
        const currentUser = this.currentUser;
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.deleteUser(currentUser, true);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.deleteUser(currentUser, true);
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

    resetPassword = (user, password) => {
        if (password != null && password.length < 3) {
            return;
        }
        if (this.pendingActionSubscription != null) {
            this.pendingActionSubscription.unsubscribe();
        }
        if (this.userApi.tokenIsFresh) {
            this.userApi.resetPassword(user, password);
        } else {
            this.loginDialog.open();
            this.pendingActionSubscription = this.freshLogin.subscribe(sucess => {
                if (sucess) {
                    this.userApi.resetPassword(user, password);
                }
            })
        }
    }

    renewLogin = () => {
        if (this.userApi.tokenIsFresh) {
            this.freshLogin.next(true);
        } else {
            this.userApi.freshLogin(this.password).pipe(take(1)).subscribe(success => {
                this.password = '';
                this.freshLogin.next(true);
            }, (err) => {
                this.password = '';
            });
        }
    }
}

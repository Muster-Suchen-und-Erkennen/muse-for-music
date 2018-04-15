import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { UserApiService } from './user-api.service';


@Injectable()
export class LoginGuard implements CanActivate {

    constructor(private router: Router, private userApi: UserApiService) { }

    canActivate() {
        if (this.userApi.loggedIn) {
            // logged in so return true
            return true;
        }

        // not logged in so redirect to login page
        this.router.navigate(['/login']);
        return false;
    }
}

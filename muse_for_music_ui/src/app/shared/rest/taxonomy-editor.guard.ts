import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { UserApiService } from './user-api.service';


@Injectable()
export class TaxonomyEditorGuard  {

    constructor(private router: Router, private userApi: UserApiService) { }

    canActivate() {
        if (this.userApi.loggedIn) {
            if (this.userApi.roles.has('taxonomy_editor')) {
                return true;
            }
            // not admin so redirect to home page
            this.router.navigate(['/']);
            return false;
        }

        // not logged in so redirect to login page
        this.router.navigate(['/login']);
        return false;
    }
}

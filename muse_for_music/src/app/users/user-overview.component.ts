import { Component, OnInit } from '@angular/core';

import { UserApiService } from '../shared/rest/user-api.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-user-overview',
  templateUrl: './user-overview.component.html',
})
export class UserOverviewComponent implements OnInit {


    constructor(private navigation: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.navigation.changeTitle('MUSE4Music – Benutzer ' + this.userApi.username);
        this.navigation.changeBreadcrumbs([new Breadcrumb('Benutzer', '/user')]);
    }
}

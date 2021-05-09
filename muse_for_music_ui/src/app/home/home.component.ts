import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { UserApiService } from '../shared/rest/user-api.service';

@Component({
  selector: 'm4m-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

    constructor(private data: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('Home');
        this.data.changeBreadcrumbs([]);
    }

    hasRole(role: string): boolean {
        return this.userApi.roles.has(role);
    }

}

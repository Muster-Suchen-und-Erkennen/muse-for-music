import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Router } from '@angular/router';
import { ApiService } from '../shared/rest/api.service';
import { UserApiService } from '../shared/rest/user-api.service';

@Component({
  selector: 'm4m-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    username: string;
    password: string = '';

    constructor(private data: NavigationService, private api: ApiService,
        private userApi: UserApiService, private router: Router) { }

    ngOnInit(): void {
        if (this.userApi.loggedIn) {
            this.router.navigate(['/']);
        }
        this.data.changeTitle('Anmelden');
        this.data.changeBreadcrumbs([]);
    }

    credentialsValid(): boolean {
        if (this.username != null && this.username.length >= 3) {
            if (this.password !== undefined && this.password !== null &&
                (this.password.length >= 3 ||
                (this.username === 'Guest' && this.password === ''))) {
                return true;
            }
        }
        return false;
    }

    login() {
        if (this.credentialsValid()) {
            this.userApi.login(this.username, this.password);
            this.password = '';
        }
    }

}

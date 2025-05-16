
import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationService } from './navigation-service';
import { UserApiService } from '../shared/rest/user-api.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'm4m-title-bar',
  templateUrl: './title-bar.component.html',
  styleUrls: ['./title-bar.component.scss']
})
export class TitleBarComponent implements OnInit, OnDestroy {

    title: string;

    private sub: Subscription|null = null;

    constructor(private data: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.sub = this.data.currentTitle.subscribe(title => this.title = title);
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    toggleEdit(): void {
        this.userApi.toggleEditing();
    }

    isLoggedIn() {
        return this.userApi.loggedIn;
    }

    canEdit() {
        return this.userApi.loggedIn && this.userApi.roles.has('user');
    }

    isEditing() {
        return this.userApi.isEditing();
    }

    logout() {
        this.userApi.logout();
    }

}

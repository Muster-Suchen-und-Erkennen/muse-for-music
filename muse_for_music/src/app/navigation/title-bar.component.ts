
import { Component, OnInit } from '@angular/core';
import { NavigationService } from './navigation-service';
import { UserApiService } from '../shared/rest/user-api.service';

@Component({
  selector: 'm4m-title-bar',
  templateUrl: './title-bar.component.html',
  styleUrls: ['./title-bar.component.scss']
})
export class TitleBarComponent implements OnInit {

    title: string;

    constructor(private data: NavigationService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.data.currentTitle.subscribe(title => this.title = title);
    }

    toggleEdit(): void {
        this.userApi.toggleEditing();
    }

}

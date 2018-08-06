import { Component, OnChanges, Input, OnInit } from '@angular/core';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { UserApiService } from '../shared/rest/user-api.service';


@Component({
  selector: 'm4m-history',
  templateUrl: './history.component.html',
})
export class HistoryComponent implements OnChanges, OnInit {

    @Input() user: string;

    history: ApiObject[];

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        if (this.userApi.roles.has('admin')) {
            this.api.getHistory().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.history = data;
            });
        }
    }

    ngOnChanges(): void {
        this.api.getHistory(this.user).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.history = data;
        });
    }
}

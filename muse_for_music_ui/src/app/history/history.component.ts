import { Component, OnChanges, Input, OnInit, OnDestroy } from '@angular/core';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { UserApiService } from '../shared/rest/user-api.service';
import { Subscription } from 'rxjs';


@Component({
  selector: 'm4m-history',
  templateUrl: './history.component.html',
})
export class HistoryComponent implements OnChanges, OnInit, OnDestroy {

    @Input() user: string;

    history: ApiObject[];

    private sub: Subscription;

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        if (this.userApi.roles.has('admin') && !this.user) {
            if (this.sub != null) {
                this.sub.unsubscribe();
            }
            this.sub = this.api.getHistory().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.history = data;
            });
        }
    }

    ngOnChanges(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
        this.sub = this.api.getHistory(this.user).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.history = data;
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }
}

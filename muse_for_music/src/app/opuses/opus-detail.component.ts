import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription } from 'rxjs/Rx';
import { UserApiService } from 'app/shared/rest/user-api.service';

@Component({
  selector: 'm4m-opus-detail',
  templateUrl: './opus-detail.component.html',
  styleUrls: ['./opus-detail.component.scss']
})
export class OpusDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private opusSubscription: Subscription;

    opusID: number;
    opus: ApiObject;

    constructor(private navigation: NavigationService, private api: ApiService, private userApi: UserApiService, private route: ActivatedRoute) { }

    update(opusID: number) {
        if (this.opusSubscription != null) {
            this.opusSubscription.unsubscribe();
        }
        this.opusID = opusID;
        this.navigation.changeTitle('Werk');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
        new Breadcrumb('"' + opusID.toString() + '"', '/opuses/' + opusID)]);
        this.opusSubscription = this.api.getOpus(opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opus = data;
            this.navigation.changeTitle('Werk: ' + data.name);
            this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
            new Breadcrumb('"' + data.name + '"', '/opuses/' + opusID)]);
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('Werk');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.opusSubscription != null) {
            this.opusSubscription.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }
}

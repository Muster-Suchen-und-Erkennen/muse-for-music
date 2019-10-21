import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription } from 'rxjs/Rx';
import { UserApiService } from 'app/shared/rest/user-api.service';

@Component({
  selector: 'm4m-part-detail',
  templateUrl: './part-detail.component.html',
  styleUrls: ['./part-detail.component.scss']
})
export class PartDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private partSubscription: Subscription;
    private opusSubscription: Subscription;

    partID: number;
    part: ApiObject;

    constructor(private navigation: NavigationService, private api: ApiService, private userApi: UserApiService, private route: ActivatedRoute) { }

    update(partID: number) {
        this.partID = partID;
        this.navigation.changeTitle('Werkausschnitt');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Werkausschnitte', '/parts'),
        new Breadcrumb('"' + partID.toString() + '"', '/parts/' + partID)]);

        if (this.partSubscription != null) {
            this.partSubscription.unsubscribe();
        }
        this.partSubscription = this.api.getPart(partID).subscribe(part => {
            if (part == undefined) {
                return;
            }
            this.part = part;
            this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
            new Breadcrumb('"' + part.opus_id.toString() + '"', '/opuses/' + part.opus_id),
            new Breadcrumb('Werkausschnitte', '/parts'),
            new Breadcrumb('"' + part.name + '"', '/parts/' + partID)]);

            if (this.opusSubscription != null) {
                this.opusSubscription.unsubscribe();
            }
            this.opusSubscription = this.api.getOpus(part.opus_id).subscribe(opus => {
                if (opus == undefined) {
                    return;
                }
                this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
                new Breadcrumb('"' + opus.name + '"', '/opuses/' + part.opus_id),
                new Breadcrumb('Werkausschnitte', '/parts'),
                new Breadcrumb('"' + part.name + '"', '/parts/' + partID)]);
            });
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('Werkausschnitt');
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
        if (this.partSubscription != null) {
            this.partSubscription.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }
}

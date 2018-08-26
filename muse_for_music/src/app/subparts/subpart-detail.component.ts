import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'm4m-subpart-detail',
  templateUrl: './subpart-detail.component.html',
  styleUrls: ['./subpart-detail.component.scss']
})
export class SubPartDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private subPartSubscription: Subscription;
    private partSubscription: Subscription;
    private opusSubscription: Subscription;

    subPartID: number;

    constructor(private navigation: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    update(subPartID: number) {
        this.subPartID = subPartID;
        this.navigation.changeTitle('Teilwerkausschnitt');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Teilwerkausschnitte', '/subparts'),
            new Breadcrumb('"' + subPartID.toString() + '"', '/subparts/' + subPartID)]);

        if (this.subPartSubscription != null) {
            this.subPartSubscription.unsubscribe();
        }
        this.subPartSubscription = this.api.getSubPart(subPartID).subscribe(subpart => {
            if (subpart == undefined) {
                return;
            }

            this.navigation.changeBreadcrumbs([new Breadcrumb('Werkausschnitte', '/parts'),
                new Breadcrumb('"' + subpart.part_id.toString() + '"', '/parts/' + subpart.part_id),
                new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID)]);
            if (this.partSubscription != null) {
                this.partSubscription.unsubscribe();
            }
            this.partSubscription = this.api.getPart(subpart.part_id).subscribe(part => {
                if (part == undefined) {
                    return;
                }
                this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
                    new Breadcrumb('"' + part.opus_id.toString() + '"', '/opuses/' + part.opus_id),
                    new Breadcrumb('Werkausschnitte', '/parts'),
                    new Breadcrumb('"' + part.name + '"', '/parts/' + part.id),
                    new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                    new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID)]);

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
                        new Breadcrumb('"' + part.name + '"', '/parts/' + part.id),
                        new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                        new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID)]);
                });
            });
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('Teilwerkausschnitt');
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
        if (this.subPartSubscription != null) {
            this.subPartSubscription.unsubscribe();
        }
    }
}

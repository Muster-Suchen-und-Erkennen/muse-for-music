import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'm4m-opus-detail',
  templateUrl: './opus-detail.component.html',
  styleUrls: ['./opus-detail.component.scss']
})
export class OpusDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private opusSubscription: Subscription;

    opusID: number;

    constructor(private navigation: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    update(opusID: number) {
        if (this.opusSubscription != null) {
            this.opusSubscription.unsubscribe();
        }
        this.opusID = opusID;
        this.navigation.changeTitle('MUSE4Music – Opus');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'),
        new Breadcrumb('"' + opusID.toString() + '"', '/opuses/' + opusID)]);
        this.opusSubscription = this.api.getOpus(opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.navigation.changeTitle('MUSE4Music – Opus: ' + data.name);
            this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'),
            new Breadcrumb('"' + data.name + '"', '/opuses/' + opusID)]);
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('MUSE4Music – Opus');
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
}

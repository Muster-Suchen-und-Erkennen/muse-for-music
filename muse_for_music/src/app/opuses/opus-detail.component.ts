import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-opus-detail',
  templateUrl: './opus-detail.component.html',
  styleUrls: ['./opus-detail.component.scss']
})
export class OpusDetailComponent implements OnInit {

    opusID: number;

    constructor(private navigation: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    update(opusID: number) {
        this.opusID = opusID;
        this.navigation.changeTitle('MUSE4Music – Opus');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'), new Breadcrumb(opusID.toString(), '/opuses/' + opusID)]);
        this.api.getOpus(opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.navigation.changeTitle('MUSE4Music – Opus: ' + data.name);
            this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'), new Breadcrumb(data.name, '/opuses/' + opusID)]);
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('MUSE4Music – Opus');
        this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

}

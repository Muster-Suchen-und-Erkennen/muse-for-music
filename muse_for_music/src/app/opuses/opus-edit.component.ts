import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-opus-edit',
  templateUrl: './opus-edit.component.html',
  styleUrls: ['./opus-edit.component.scss']
})
export class OpusEditComponent implements OnInit {

    opus: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    constructor(private navigation: NavigationService, private api: ApiService, private route: ActivatedRoute) { }

    update(opusID: number) {
        this.navigation.changeTitle('MUSE4Music – Opus');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'), new Breadcrumb(opusID.toString(), '/opuses/' + opusID)]);
        this.api.getOpus(opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.navigation.changeTitle('MUSE4Music – Opus: ' + data.name);
            this.navigation.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses'), new Breadcrumb(data.name, '/opuses/' + opusID)]);
            this.opus = data;
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('MUSE4Music – Opus');
        this.route.params.subscribe(params => {
            this.update(parseInt(params['id'], 10));
        });
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    save(event) {
        if (this.valid) {
            this.api.putPerson(this.opus.id, this.data);
        }
    }

}

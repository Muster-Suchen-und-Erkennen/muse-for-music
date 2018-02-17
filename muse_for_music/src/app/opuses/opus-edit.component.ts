import { Component, OnChanges, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-opus-edit',
  templateUrl: './opus-edit.component.html',
  styleUrls: ['./opus-edit.component.scss']
})
export class OpusEditComponent implements OnChanges {

    @Input() opusID: number;

    opus: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    constructor(private api: ApiService) { }

    ngOnChanges(): void {
        this.api.getOpus(this.opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opus = data;
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
            this.api.putOpus(this.opus.id, this.data);
        }
    }

}

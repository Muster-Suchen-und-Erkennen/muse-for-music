import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-subpart-edit',
  templateUrl: './subpart-edit.component.html',
  styleUrls: ['./subpart-edit.component.scss']
})
export class SubPartEditComponent implements OnChanges {

    @Input() subPartID: number;

    subpart: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        this.api.getSubPart(this.subPartID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.subpart = data;
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
            this.api.putSubPart(this.subpart.id, this.data);
        }
    }

    delete = (() => {
        //this.api.deleteSubPart(this.subpart).take(1).subscribe(() => this.router.navigate(['parts', this.subpart.part_id]));
    }).bind(this);

}

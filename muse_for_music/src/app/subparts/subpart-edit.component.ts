import { Component, OnChanges, Input, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { take } from 'rxjs/operators';

@Component({
  selector: 'm4m-subpart-edit',
  templateUrl: './subpart-edit.component.html',
  styleUrls: ['./subpart-edit.component.scss']
})
export class SubPartEditComponent implements OnChanges {

    @Input() subPartID: number;

    @ViewChild(DynamicFormComponent, {static: false}) form;

    subpart: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        this.api.getSubPart(this.subPartID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.subpart = data;
        });
    }

    save = (event) => {
        this.api.putSubPart(this.subpart.id, event).pipe(take(1)).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteSubPart(this.subpart).pipe(take(1)).subscribe(() => this.router.navigate(['parts', this.subpart.part_id]));
    };

}

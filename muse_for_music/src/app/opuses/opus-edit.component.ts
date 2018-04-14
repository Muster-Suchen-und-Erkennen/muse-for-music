import { Component, OnChanges, Input, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';

@Component({
  selector: 'm4m-opus-edit',
  templateUrl: './opus-edit.component.html',
  styleUrls: ['./opus-edit.component.scss']
})
export class OpusEditComponent implements OnChanges {

    @Input() opusID: number;

    @ViewChild(DynamicFormComponent) form;

    opus: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        this.api.getOpus(this.opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opus = data;
        });
    }

    save = (event) => {
        this.api.putOpus(this.opus.id, event).take(1).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteOpus(this.opusID).take(1).subscribe(() => this.router.navigate(['opuses']));
    };

}

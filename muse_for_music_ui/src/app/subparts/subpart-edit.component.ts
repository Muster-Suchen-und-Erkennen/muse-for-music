import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { take } from 'rxjs/operators';
import { Subscription } from 'rxjs';

@Component({
  selector: 'm4m-subpart-edit',
  templateUrl: './subpart-edit.component.html',
  styleUrls: ['./subpart-edit.component.scss']
})
export class SubPartEditComponent implements OnChanges, OnDestroy {

    @Input() subPartID: number;

    @ViewChild(DynamicFormComponent) form;

    subpart: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    private sub: Subscription|null = null;

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
        this.sub = this.api.getSubPart(this.subPartID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.subpart = data;
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
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

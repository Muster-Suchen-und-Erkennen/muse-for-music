import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { take } from 'rxjs/operators';
import { Subscription } from 'rxjs';

@Component({
  selector: 'm4m-part-edit',
  templateUrl: './part-edit.component.html',
  styleUrls: ['./part-edit.component.scss']
})
export class PartEditComponent implements OnChanges, OnDestroy {

    @Input() partID: number;
    @ViewChild(DynamicFormComponent) form;

    part: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    private sub: Subscription|null = null;

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
        this.sub = this.api.getPart(this.partID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.part = data;
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    save = (event) => {
        this.api.putPart(this.part.id, event).pipe(take(1)).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deletePart(this.part).pipe(take(1)).subscribe(() => this.router.navigate(['opuses', this.part.opus_id]));
    };

}

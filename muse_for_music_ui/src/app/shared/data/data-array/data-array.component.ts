import { Component, Input, OnChanges } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';

@Component({
    selector: 'data-array',
    templateUrl: './data-array.component.html'
})
export class DataArrayComponent implements OnChanges {

    @Input() property: ApiModel|ApiModelRef;
    @Input() model: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() context: any;

    open: boolean = false;

    items: ApiModel;

    constructor(private models: ModelsService) { }

    ngOnChanges(changes): void {
        if (changes.model != null) {
            if (this.model.items.$ref != null) {
                this.models.getModel(this.model.items.$ref).subscribe(items => this.items = items);
            } else {
                this.items = this.model.items;
            }
        }
    }

    reference(): string {
        if (this.model == null || this.model['x-reference'] == null) {
            return null;
        }
        return this.model['x-reference'];
    }

    trackByFn(index, item) {
        return item['x-key'];
    }

}

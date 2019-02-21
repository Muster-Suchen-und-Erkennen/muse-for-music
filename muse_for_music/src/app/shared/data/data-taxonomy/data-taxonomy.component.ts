import { Component, Input } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';

@Component({
    selector: 'data-taxonomy',
    templateUrl: './data-taxonomy.component.html'
})
export class DataTaxonomyComponent {

    @Input() property: ApiModel|ApiModelRef;
    @Input() model: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() context: any;

    constructor() { }

    taxonomy(): string {
        if (this.model == null || this.model['x-taxonomy'] == null) {
            return null;
        }
        return this.model['x-taxonomy'];
    }

    trackByFn(index, item) {
        return item.id;
    }

}

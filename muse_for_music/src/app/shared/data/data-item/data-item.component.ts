import { Component, Input, OnChanges } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';

@Component({
    selector: 'data-item',
    templateUrl: './data-item.component.html'
})
export class DataItemComponent implements OnChanges {

    @Input() property: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() context: any;

    model: ApiModel|ApiModelRef;
    open: boolean = false;

    constructor(private models: ModelsService) { }

    ngOnChanges(changes): void {
        if (changes.property != null) {
            if ((this.property as ApiModelRef).$ref != null) {
                this.models.getModel((this.property as ApiModelRef).$ref).subscribe(model => {
                    this.model = model;
                });
            } else {
                this.model = this.property;
            }
        }
    }

    type(): string {
        if (this.model == null || this.model.type == null) {
            return null;
        }
        let type = this.model.type;
        if (type === 'string') {
            if (this.model.enum != null) {
                type = 'enum';
            }
        }
        if (type === 'object' || type === 'array') {
            if (this.model['x-reference'] != null) {
                type = 'reference';
            } else if (this.model['x-taxonomy'] != null) {
                type = 'taxonomy';
            }
        }
        return type;
    }

    isCollapsible() {
        return false;
    }

    toggleOpen() {
        return;
    }

}

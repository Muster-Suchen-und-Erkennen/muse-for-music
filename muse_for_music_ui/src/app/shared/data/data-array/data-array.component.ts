import { Component, Input, OnChanges, OnDestroy } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'data-array',
    templateUrl: './data-array.component.html'
})
export class DataArrayComponent implements OnChanges, OnDestroy {

    @Input() property: ApiModel|ApiModelRef;
    @Input() model: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() context: any;

    open: boolean = false;

    items: ApiModel;

    private sub: Subscription|null = null;

    constructor(private models: ModelsService) { }

    ngOnChanges(changes): void {
        if (changes.model != null) {
            if (this.model.items.$ref != null) {
                if (this.sub != null) {
                    this.sub.unsubscribe();
                }
                this.sub = this.models.getModel(this.model.items.$ref).subscribe(items => this.items = items);
            } else {
                this.items = this.model.items;
            }
        }
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
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

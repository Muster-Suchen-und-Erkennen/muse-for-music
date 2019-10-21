import { Component, Input, OnChanges } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { Router } from '@angular/router';

@Component({
    selector: 'data-reference',
    templateUrl: './data-reference.component.html'
})
export class DataReferenceComponent implements OnChanges {

    @Input() property: ApiModel|ApiModelRef;
    @Input() model: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() context: any;

    open: boolean = false;

    properties: (ApiModel | ApiModelRef)[];

    constructor(private router: Router) { }

    ngOnChanges(changes): void {
      if (changes.model != null) {
          const props = [];
            if (this.model.properties != null) {
                for (const key in this.model.properties) {
                    if (!this.model.properties.hasOwnProperty(key)) {
                        continue;
                    }
                    if (key === '_links' || key === '_embedded') {
                        continue;
                    }
                    if (this.model.properties[key].readOnly != null && this.model.properties[key].readOnly) {
                        continue;
                    }
                    props.push(this.model.properties[key]);
                }
            }
            this.properties = props.sort((a, b) => {
                const orderA = a['x-order'] != null ? a['x-order'] : 0;
                const orderB = b['x-order'] != null ? b['x-order'] : 0;
                return orderA - orderB;
            });
        }
    }

    reference(): string {
        if (this.property != null) {
            const ref = this.property.$ref;
            if (ref === '#/definitions/PersonGET') {
                return 'person';
            }
        }
        if (this.model == null || this.model['x-reference'] == null) {
            return null;
        }
        return this.model['x-reference'];
    }

    navigateToReference() {
        const ref = this.reference();
        if (ref == null) {
            return;
        }
        if (ref === 'person') {
            if (this.data == null || this.data.id == null) {
                return;
            }
            this.router.navigate(['/people']);
        }
    }

    trackByFn(index, item) {
        return item['x-key'];
    }

}

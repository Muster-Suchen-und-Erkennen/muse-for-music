import { Component, Input, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild } from '@angular/core';

import { Subscription } from 'rxjs/Rx';

import { ApiObject } from '../../rest/api-base.service';
import { ModelsService } from 'app/shared/rest/models.service';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';

@Component({
    selector: 'dynamic-data',
    templateUrl: './dynamic-data.component.html'
})
export class DynamicDataComponent implements OnChanges {

    @Input() modelUrl: string;
    @Input() filter: string[] = [];
    @Input() isBlacklist: boolean = false;
    @Input() data: ApiObject;
    @Input() context: any;

    @Input() title: string;

    model: ApiModel;
    properties: (ApiModel | ApiModelRef)[];

    constructor(private models: ModelsService) { }

    ngOnChanges(changes: SimpleChanges): void {
      if (changes.modelUrl != null || changes.filter != null || changes.isBlacklist != null) {

        this.models.getModel(this.modelUrl)
            .map(this.models.filterModel(this.filter, this.isBlacklist))
            .first().subscribe(model => {
              const props = [];
              if (model.properties != null) {
                  for (const key in model.properties) {
                      if (!model.properties.hasOwnProperty(key)) {
                          continue;
                      }
                      if (key === '_links' || key === '_embedded') {
                          continue;
                      }
                      if (model.properties[key].readOnly != null && model.properties[key].readOnly) {
                          continue;
                      }
                      props.push(model.properties[key]);
                  }
              }
              if (model.title != null) {
                  this.title = model.title;
              }
              this.model = model;
              this.properties = props.sort((a, b) => {
                  const orderA = a['x-order'] != null ? a['x-order'] : 0;
                  const orderB = b['x-order'] != null ? b['x-order'] : 0;
                  return orderA - orderB;
              });
        });
      }
    }

    trackByFn(index, item) {
        return item['x-key'];
    }

}

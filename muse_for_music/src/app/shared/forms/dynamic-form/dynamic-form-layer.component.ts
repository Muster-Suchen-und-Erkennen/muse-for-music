import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { FormGroupService } from '../form-group.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'df-layer',
    templateUrl: './dynamic-form-layer.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DynamicFormLayerComponent implements OnChanges {

    @Input() modelUrl: string;
    @Input() filter: string[] = [];
    @Input() isBlacklist: boolean = false;

    @Input() path: string = '';
    @Input() startData: any;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() validForSave: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Input() specifications = [];
    @Input() specificationsCallback: (path: string, remove: boolean, recursive: boolean, affectsArrayMembers: boolean) => void;

    @Input() context: any;

    @Input() debug: boolean = true;

    model: ApiModel;
    properties: (ApiModel | ApiModelRef)[];
    form: FormGroup;

    private lastValid: boolean = false;

    private formSubscription: Subscription;

    constructor(private models: ModelsService, private formGroups: FormGroupService, private changeDetector: ChangeDetectorRef) {}

    private runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.modelUrl != null || changes.filter != null || changes.isBlacklist != null) {
            if (this.modelUrl == null) {
                return;
            }

            this.models.getModel(this.modelUrl)
                .map(this.models.filterModel(this.filter, this.isBlacklist))
                .first().subscribe(model => {
                    const props = [];
                    if (model.properties != null) {
                        for (const key in model.properties) {
                            if (!model.properties.hasOwnProperty(key)) {
                                continue;
                            }
                            props.push(model.properties[key]);
                        }
                    }
                    this.model = model;
                    this.properties = props.sort((a, b) => {
                        const orderA = a['x-order'] != null ? a['x-order'] : 0;
                        const orderB = b['x-order'] != null ? b['x-order'] : 0;
                        return orderA - orderB;
                    });
                    this.form = this.formGroups.toFormGroup(model);
                    if (this.startData != null) {
                        this.form.patchValue(this.startData);
                    }
                    if (this.formSubscription != null) {
                        this.formSubscription.unsubscribe();
                    }
                    this.formSubscription = this.form.statusChanges.subscribe(status => {
                        this.valid.emit(this.form.valid);
                        this.data.emit(this.form.value);
                        if (this.lastValid !== this.form.valid) {
                            // only run change detection on this level for changes in valid status
                            // ignore value changes here
                            this.runChangeDetection();
                        }
                        this.lastValid = this.form.valid;
                    });
                    this.valid.emit(this.form.valid);
                    this.runChangeDetection();
                });
        }
        if (changes.startData != null) {
            if (this.startData != null && this.form != null) {
                this.form.patchValue(this.startData);

                // don't run change detection here as this component can not
                // efficiently decide if changes in start data happened from
                // outside or from within the form
            }
        }
        if (changes.path != null || changes.context != null || changes.debug != null) {
            this.runChangeDetection();
        }
    }

    trackBy(index, model: ApiModel) {
        return model['x-key'];
    }
}

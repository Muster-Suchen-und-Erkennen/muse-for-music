
import {first, map, debounceTime, take} from 'rxjs/operators';
import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, ChangeDetectionStrategy, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { FormGroupService } from '../form-group.service';
import { Subscription, Subject } from 'rxjs';
import { SpecificationUpdateEvent } from './specification-update-event';

@Component({
    selector: 'df-layer',
    templateUrl: './dynamic-form-layer.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DynamicFormLayerComponent implements OnChanges, OnDestroy {

    @Input() modelUrl: string;
    @Input() filter: string[] = [];
    @Input() isBlacklist: boolean = false;

    @Input() path: string = '';
    @Input() startData: any;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() validForSave: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Input() specifications = [];
    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();

    @Input() context: any;

    @Input() debug: boolean = false;

    model: ApiModel;
    properties: (ApiModel | ApiModelRef)[];
    form: UntypedFormGroup;

    private changeDetectionBatchSubject: Subject<null> = new Subject<null>();

    private lastValid: boolean = false;

    private formSubscription: Subscription|null = null;
    private changeSub: Subscription|null = null;

    constructor(private models: ModelsService, private formGroups: FormGroupService, private changeDetector: ChangeDetectorRef) {
        this.changeSub = this.changeDetectionBatchSubject.asObservable().pipe(debounceTime(50)).subscribe(() => this.runChangeDetection());
    }

    private runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.modelUrl != null || changes.filter != null || changes.isBlacklist != null) {
            if (this.modelUrl == null) {
                return;
            }

            this.models.getModel(this.modelUrl).pipe(
                map(this.models.filterModel(this.filter, this.isBlacklist)),
                map(this.models.filterModel(['specifications'], true)),
                first(),
                take(1),
            ).subscribe(model => {
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
                        this.data.emit(this.form.value);
                        this.updateValidStatus();
                    });
                    this.data.emit(this.form.value);
                    this.updateValidStatus();
                    this.runChangeDetection();
                });
        }
        if (changes.startData != null) {
            if (this.startData != null && this.form != null) {
                this.form.patchValue(this.startData);

                // debounce all change detection here as this component can not
                // efficiently decide if changes in start data happened from
                // outside or from within the form
                this.changeDetectionBatchSubject.next();
            }
        }
        if (changes.path != null || changes.context != null || changes.debug != null) {
            this.runChangeDetection();
        }
    }

    ngOnDestroy(): void {
        if (this.changeSub != null) {
            this.changeSub.unsubscribe();
        }
        if (this.formSubscription != null) {
            this.formSubscription.unsubscribe();
        }
        this.changeDetectionBatchSubject.unsubscribe();
    }

    private updateValidStatus() {
        this.valid.emit(this.form.valid);
        let validForSave = true;
        this.properties.forEach(prop => {
            const control = this.form.get(prop['x-key']);
            if (control == null || (!control.valid && !prop['x-allowSave'])) {
                validForSave = false;
            }
        });
        this.validForSave.emit(validForSave);
        if (this.lastValid !== this.form.valid) {
            // only run change detection on this level for changes in valid status
            // ignore value changes here
            this.runChangeDetection();
        }
        this.lastValid = this.form.valid;
    }

    trackBy(index, model: ApiModel) {
        return model['x-key'];
    }
}

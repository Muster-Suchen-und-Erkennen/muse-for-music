
import {take} from 'rxjs/operators';
import { Component, forwardRef, Input, OnInit, OnChanges, AfterViewInit, ViewChild, Output, EventEmitter, OnDestroy } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, NG_ASYNC_VALIDATORS, AsyncValidator, Validator, NG_VALIDATORS } from '@angular/forms';

import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { DynamicFormLayerComponent } from '../dynamic-form-layer.component';
import { Subject, BehaviorSubject, Subscription } from 'rxjs';
import { ModelsService } from 'app/shared/rest/models.service';
import { SpecificationUpdateEvent } from '../specification-update-event';



@Component({
  selector: 'm4m-object-input',
  templateUrl: 'object-input.component.html',
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => ObjectInputComponent),
    multi: true
  }, {
    provide: NG_VALIDATORS,
    useExisting: ObjectInputComponent,
    multi: true
  }]
})
export class ObjectInputComponent implements ControlValueAccessor, OnInit, AfterViewInit, Validator, OnDestroy {

    @ViewChild(DynamicFormLayerComponent) formLayer: DynamicFormLayerComponent;

    @Input() property: ApiModel|ApiModelRef;
    @Input() path: string;
    @Input() context: any;
    @Input() debug: boolean = false;

    @Input() specifications = [];
    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();

    model: ApiModel;

    currentValue: any;

    valid: boolean = false;

    onChange: any = () => {};

    onTouched: any = () => {};

    validator: any = () => { };

    private sub: Subscription|null = null;

    constructor(private models: ModelsService) {}

    get value(): any {
        if (this.currentValue == null || this.currentValue === '') {
            return this.nullValue;
        } else {
            return this.currentValue;
        }
    }

    set value(val: any) {
        let newVal;
        if (val === this.nullValue) {
            newVal = undefined;
        } else {
            newVal = {...val};
        }
        if (newVal == undefined && this.currentValue == undefined) {
            return;
        }
        if (JSON.stringify(newVal) === JSON.stringify(this.currentValue)) {
            return;
        }
        this.currentValue = newVal;
        this.onChange(val);
        this.onTouched();
    }

    get nullValue() {
        if (this.model != null && this.model.hasOwnProperty('x-nullValue')) {
            return this.model['x-nullValue'];
        }
        return {id: -1};
    }

    updateValue(event) {
        this.currentValue = event;
        this.onChange(this.value);
        this.onTouched();
    }

    registerOnChange(fn) {
        this.onChange = fn;
    }

    registerOnTouched(fn) {
        this.onTouched = fn;
    }

    writeValue(value) {
        if (value) {
            this.value = value;
        }
    }

    validate() {
        if (this.valid) {
            return null;
        } else {
            return {nestedError: 'A nested form has an error.'};
        }
    }

    ngOnInit() {
        const modelUrl = this.property.$ref;
        this.models.getModel(modelUrl).pipe(take(1)).subscribe(model => {
            this.model = model;
        });
    }

    ngAfterViewInit(): void {
        this.sub = this.formLayer.valid.subscribe((valid) => {
            this.valid = valid;
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }
}

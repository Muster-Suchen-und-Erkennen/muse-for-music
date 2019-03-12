import { Component, forwardRef, Input, OnInit, OnChanges, AfterViewInit, ViewChild } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, NG_ASYNC_VALIDATORS, AsyncValidator, Validator, NG_VALIDATORS } from '@angular/forms';

import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { DynamicFormLayerComponent } from '../dynamic-form-layer.component';
import { Subject, BehaviorSubject, Subscription } from 'rxjs';
import { ModelsService } from 'app/shared/rest/models.service';



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
export class ObjectInputComponent implements ControlValueAccessor, OnInit, AfterViewInit, Validator  {

    @ViewChild(DynamicFormLayerComponent) formLayer: DynamicFormLayerComponent;

    @Input() property: ApiModel|ApiModelRef;
    @Input() path: string;
    @Input() context: any;

    @Input() specifications = [];
    @Input() specificationsCallback: (path: string, remove: boolean, recursive: boolean, affectsArrayMembers: boolean) => void;

    model: ApiModel;

    currentValue: any;

    valid: boolean = false;

    onChange: any = () => {};

    onTouched: any = () => {};

    validator: any = () => { };

    constructor(private models: ModelsService) {}

    get value(): any {
        if (this.currentValue == null || this.currentValue === '') {
            return this.nullValue;
        } else {
            return this.currentValue;
        }
    }

    set value(val: any) {
        if (val === this.nullValue) {
            this.currentValue = undefined;
        } else {
            this.currentValue = val;
        }
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
        this.models.getModel(modelUrl).take(1).subscribe(model => {
            this.model = model;
        });
    }

    ngAfterViewInit(): void {
        this.formLayer.valid.subscribe((valid) => {
            this.valid = valid;
        });
    }
}


import {map} from 'rxjs/operators';
import { Component, forwardRef, Input, OnInit, ViewChildren, AfterViewInit, Output, EventEmitter } from '@angular/core';

import { ApiModel } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { DynamicFormLayerComponent } from '../dynamic-form-layer.component';
import { combineLatest, Observable, Subscription } from 'rxjs';
import { NG_VALUE_ACCESSOR, NG_VALIDATORS, ControlValueAccessor, Validator } from '@angular/forms';
import { SpecificationUpdateEvent } from '../specification-update-event';




@Component({
  selector: 'm4m-array-input',
  templateUrl: 'array-input.component.html',
  styleUrls: ['array-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => ArrayInputComponent),
    multi: true
  }, {
    provide: NG_VALIDATORS,
    useExisting: ArrayInputComponent,
    multi: true
  }]
})
export class ArrayInputComponent implements ControlValueAccessor, AfterViewInit, Validator {

    constructor(private models: ModelsService) {}

    @ViewChildren(DynamicFormLayerComponent) formLayers;

    @Input() property: ApiModel;
    @Input() path: string;
    @Input() context: any;
    @Input() debug: boolean = false;

    @Input() specifications = [];
    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();


    currentValue: any[] = [];

    lastValidSub: Subscription;
    valid: boolean = false;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): any {
        if (this.currentValue == null) {
            return this.nullValue;
        } else {
            return this.currentValue;
        }
    }

    set value(val: any) {
        if (val === this.nullValue) {
            this.currentValue = [];
        } else {
            this.currentValue = val;
        }
        this.onChange(val);
        this.onTouched();
    }

    get nullValue() {
        if (this.property != null && this.property.hasOwnProperty('x-nullValue')) {
            return this.property['x-nullValue'];
        }
        return [];
    }

    updateValue(index, event) {
        this.currentValue[index] = event;
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
        if (this.valid || (this.value != null && this.value.length === 0)) {
            return null;
        } else {
            return {nestedError: 'A nested form has an error.'};
        }
    }

    trackBy(index) {
        return index;
    }

    ngAfterViewInit(): void {
        this.formLayers.changes.subscribe((forms) => {
          const micoForms: DynamicFormLayerComponent[] = forms._results;
          const validObservables: Observable<boolean>[] = [];
          let currentlyValid = true;
          micoForms.forEach((form) => {
              validObservables.push(form.valid.asObservable());
              if (!form.form.valid) {
                  currentlyValid = false;
              }
          });
          if (this.lastValidSub != null) {
              this.lastValidSub.unsubscribe();
          }
          if (validObservables.length > 0) {
              this.lastValidSub = combineLatest(...validObservables).pipe(map((values) => {
                  return !values.some(value => !value);
              })).subscribe((valid) => this.valid = valid);
          }
          this.valid = currentlyValid;
      });
    }

    newItem() {
        this.currentValue.push(null);
        this.valid = false; // heuristic that assumes new item is invalid at first
        this.onChange(this.value);
        this.onTouched();
    }

    deleteItem(i) {
        this.currentValue.splice(i, 1);
        this.specificationsUpdate.emit({path: this.path + '.' + i, remove: true, recursive: true, affectsArrayMembers: true});
        this.onChange(this.value);
        this.onTouched();
    }

}

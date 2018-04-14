import { Component, forwardRef, Input, ViewChild } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { ChangeDetectorRef } from '@angular/core';

import { ApiObject } from '../../../rest/api-base.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';



@Component({
  selector: 'm4m-taxonomy-select',
  templateUrl: 'taxonomy-select.component.html',
  styleUrls: ['taxonomy-select.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => TaxonomySelectComponent),
    multi: true
  }]
})
export class TaxonomySelectComponent implements ControlValueAccessor {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent

    @Input('value') _value: any[] = [];
    @Input() question: QuestionBase<any>;

    searchTerm: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): ApiObject|ApiObject[] {
        if (!this.question.isArray) {
            if (this._value == undefined || this._value.length === 0) {
                return this.question.nullValue;
            }
            return this._value[0];
        }
        if (this._value == undefined) {
            this._value = [];
        }
        return this._value;
    }

    set value(val: ApiObject|ApiObject[]) {
        if (val == undefined) {
            this._value = []
        } else {
            if (!this.question.isArray) {
                if ((val as ApiObject).id === -1) {
                    this._value = [];
                    val = null;
                } else {
                    this._value = [val];
                }
            } else {
                this._value = (val as ApiObject[]);
            }
        }
        this.onChange(this.value);
        this.onTouched();
    }

    constructor(private cdRef:ChangeDetectorRef) {}

    selectedList() {
        return this._value;
    }

    selectedChange(selected: ApiObject[]) {
        this._value = selected;
        if (!this.question.isArray) {
            this.dropdown.closeDropdown();
        }
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
}

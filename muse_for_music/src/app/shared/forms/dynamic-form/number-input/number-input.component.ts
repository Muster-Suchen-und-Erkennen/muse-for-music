import { Component, forwardRef, Input, OnInit, OnChanges } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiModel } from 'app/shared/rest/api-model';



@Component({
  selector: 'm4m-number-input',
  templateUrl: 'number-input.component.html',
  styleUrls: ['number-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => NumberInputComponent),
    multi: true
  }]
})
export class NumberInputComponent implements ControlValueAccessor {

    @Input('value') _value: string = undefined;
    @Input() question: ApiModel;
    @Input() path: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): number {
        if (this._value == null || this._value === '') {
            return this.nullValue;
        } else {
            if (this.question.valueType === 'integer') {
                return parseInt(this._value, 10);
            } else {
                return parseFloat(this._value);
            }
        }
    }

    set value(val: number) {
        if (val === this.nullValue) {
            this._value = undefined;
        } else {
            this._value = val.toString();
        }
        this.onChange(val);
        this.onTouched();
    }

    get nullValue() {
        if (this.question != null && this.question.hasOwnProperty('x-nullValue')) {
            return this.question['x-nullValue'];
        }
        return -1;
    }

    updateValue(event) {
        this._value = event;
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

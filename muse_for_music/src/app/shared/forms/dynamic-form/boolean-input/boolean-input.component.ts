import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiModel } from 'app/shared/rest/api-model';



@Component({
  selector: 'm4m-boolean-input',
  templateUrl: 'boolean-input.component.html',
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => BooleanInputComponent),
    multi: true
  }]
})
export class BooleanInputComponent implements ControlValueAccessor {

    @Input() question: ApiModel;
    @Input() path: string;
    checked: boolean = false;

    onChange: any = () => {};

    onTouched: any = () => {};

    @Input() get value(): boolean {
        return !(!this.checked)
    }

    set value(val: boolean) {
        this.checked = val;
        this.onChange(val);
        this.onTouched();
    }

    onClick() {
        this.checked = !this.checked;
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

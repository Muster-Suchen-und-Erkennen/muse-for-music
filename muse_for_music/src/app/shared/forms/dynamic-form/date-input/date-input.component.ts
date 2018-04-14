import { Component, forwardRef, Input, OnInit, OnChanges } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { QuestionBase } from '../../question-base';



@Component({
  selector: 'm4m-date-input',
  templateUrl: 'date-input.component.html',
  styleUrls: ['date-input.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => DateInputComponent),
    multi: true
  }]
})
export class DateInputComponent implements ControlValueAccessor {

    inputValue: string = '';

    @Input() question: QuestionBase<any>;

    onChange: any = () => {};

    onTouched: any = () => {};

    @Input()
    get value(): string {
        if (this.inputValue == null || this.inputValue === '') {
            return this.question.nullValue;
        }
        return this.inputValue;
    }

    set value(val: string) {
        if (val === this.question.nullValue) {
            this.inputValue = '';
        }
        this.onChange(val);
        this.onTouched();
    }

    updateValue(event) {
        this.inputValue = event;
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

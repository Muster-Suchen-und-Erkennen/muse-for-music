import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { QuestionBase } from '../../question-base';

@Component({
  selector: 'm4m-reference-chooser',
  templateUrl: 'reference-chooser.component.html',
  styleUrls: ['reference-chooser.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => ReferenceChooserComponent),
    multi: true
  }]
})
export class ReferenceChooserComponent implements ControlValueAccessor, OnInit {
    @Input('value') _value: number = undefined;
    @Input() question: QuestionBase<any>;

    choices: {[propName: number]: ApiObject};

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): ApiObject {
        if (this.choices == undefined || this._value == undefined) {
            return {_links: {self: {href: ''}}, id: -1}
        }
        let value = this.choices[this._value];
        if (value == undefined) {
            return {_links: {self: {href: ''}}, id: -1}
        }
        return value;
    }

    set value(val: ApiObject) {
        if (val == undefined || val.id == undefined) {
            this._value = -1;
        } else {
            this._value = val.id;
        }
        this.onChange(val);
        this.onTouched();
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        if (this.question.valueType === 'person') {
            this.api.getPeople().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = {};
                for (let choice of data) {
                    this.choices[choice.id] = choice;
                }
            });
        };
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

import { Component, forwardRef, Input, OnInit, ViewChild } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';



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

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent

    @Input('value') _value: any = undefined;
    @Input() question: QuestionBase<any>;

    searchTerm: string;

    choices: ApiObject[];

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): ApiObject {
        if (this.choices == undefined || this._value == undefined) {
            return {_links: {self: {href: ''}}, id: -1}
        }
        return this._value;
    }

    set value(val: ApiObject) {
        this._value = val;
        this.onChange(val);
        this.onTouched();
        if (val.id != -1) {
            this.searchTerm = val.name;
        }
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        if (this.question.valueType === 'person') {
            this.api.getPeople().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
            });
        };
    }

    selectedChange(selected: ApiObject) {
        this.value = selected;
        this.dropdown.closeDropdown();
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

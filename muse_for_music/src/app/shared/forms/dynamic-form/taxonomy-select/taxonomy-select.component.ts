import { Component, forwardRef, Input, ViewChild } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

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

    @Input('value') _value: any = undefined;
    @Input() question: QuestionBase<any>;

    searchTerm: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    get value(): ApiObject {
        if (this._value == undefined) {
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

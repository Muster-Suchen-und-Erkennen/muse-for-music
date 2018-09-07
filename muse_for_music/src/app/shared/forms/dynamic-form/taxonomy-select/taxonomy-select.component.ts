import { Component, forwardRef, Input, ViewChild, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { ApiService } from '../../../rest/api.service';



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
export class TaxonomySelectComponent implements ControlValueAccessor, OnInit {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent

    _value: any[] = [];
    @Input() question: QuestionBase<any>;
    @Input() path: string;

    @Input() specificationsCallback: (path: string, remove: boolean, recursive: boolean, affectsArrayMembers: boolean) => void;

    specification: any;
    _specifications: Map<number, any> = new Map<number, any>();
    @Input()
    set specifications(specifications: any[]) {
        const newSpecs =  new Map<number, any>();
        specifications.forEach((spec) => {
            if (this.question.isArray) {
                if (spec.path.startsWith(this.path)) {
                    if (spec.path.length > this.path.length) {
                        const id = parseInt(spec.path.substring(this.path.length + 1), 10);
                        newSpecs.set(id, spec);
                    }
                }
            } else {
                if (spec.path === this.path) {
                    this.specification = spec;
                }
            }
        });
        this._specifications = newSpecs;
    }

    displayName: string;

    searchTerm: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    @Input()
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

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        this.api.getTaxonomy(this.question.valueType).subscribe(taxonomy => {
            if (taxonomy == undefined) {
                return;
            }
            this.displayName = taxonomy.name;
            if (taxonomy.display_name) {
                this.displayName = taxonomy.display_name;
            }
        });
    }

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

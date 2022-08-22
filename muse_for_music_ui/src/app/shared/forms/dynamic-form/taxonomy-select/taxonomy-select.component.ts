import { Component, forwardRef, Input, ViewChild, OnInit, OnChanges, SimpleChanges, ChangeDetectionStrategy, ChangeDetectorRef, Output, EventEmitter } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';

import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { ApiService } from '../../../rest/api.service';
import { SpecificationUpdateEvent } from '../specification-update-event';
import { ApiModel } from 'app/shared/rest/api-model';



@Component({
  selector: 'm4m-taxonomy-select',
  templateUrl: 'taxonomy-select.component.html',
  styleUrls: ['taxonomy-select.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => TaxonomySelectComponent),
    multi: true
  }],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TaxonomySelectComponent implements ControlValueAccessor, OnInit, OnChanges {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent

    _value: any[] = [];
    @Input() question: ApiModel;
    @Input() path: string;

    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();

    specification: any;
    specificationMap: Map<number, any> = new Map<number, any>();
    @Input() specifications: any[] = [];


    displayName: string;

    searchTerm: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    selectableId(index, selectable) {
        return selectable.id;
    }

    @Input()
    get value(): ApiObject|ApiObject[] {
        if (!this.isArray) {
            if (this._value == undefined || this._value.length === 0) {
                return this.nullValue;
            }
            return this._value[0];
        }
        if (this._value == undefined) {
            this._value = this.nullValue;
        }
        return this._value;
    }

    set value(val: ApiObject|ApiObject[]) {
        if (val == undefined) {
            this._value = []
        } else {
            if (!this.isArray) {
                if ((val as ApiObject).id === this.nullValue.id) {
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

    get isArray(): boolean {
        return this.question != null && this.question['x-isArray'];
    }

    get nullValue(): any {
        if (this.isArray) {
            return [];
        } else {
            if (this.question != null && this.question.hasOwnProperty('x-nullValue')) {
                return this.question['x-nullValue'];
            }
            return {id: -1};
        }
    }

    constructor(private api: ApiService, private changeDetector: ChangeDetectorRef) {}

    private runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnInit(): void {
        this.api.getTaxonomy(this.question['x-taxonomy']).subscribe(taxonomy => {
            if (taxonomy == undefined) {
                return;
            }
            this.displayName = taxonomy.name;
            if (taxonomy.display_name) {
                this.displayName = taxonomy.display_name;
            }
            this.runChangeDetection();
        });
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.specifications != null || changes.path != null) {
            this.updateSpecificationMap();
            this.runChangeDetection();
        }
    }

    updateSpecificationMap() {
        const newSpecs =  new Map<number, any>();
        this.specification = undefined;
        this.specifications.forEach((spec) => {
            if (this.isArray) {
                if (spec.path.startsWith(this.path)) {
                    if (spec.path.length > this.path.length) {
                        const id = parseInt(spec.path.substring(this.path.length + 1), 10);
                        newSpecs.set(id, spec);
                    }
                }
            } else {
                console.log('path: '+spec.path, 'should: ' + this.path)
                if (spec.path === this.path) {
                    this.specification = spec;
                }
            }
        });
        this.specificationMap = newSpecs;
    }

    editSpecification(id) {
        this.specificationsUpdate.emit({path: this.path + (this.isArray ? '.' + id : '')});
    }

    removeSpecification(id) {
        this.specificationsUpdate.emit({path: this.path + (this.isArray ? '.' + id : ''), remove: true});
    }

    selectedList() {
        return this._value;
    }

    selectedChange(selected: ApiObject[]) {
        this._value = selected;
        if (!this.isArray) {
            this.dropdown.closeDropdown();
        }
        this.runChangeDetection();
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

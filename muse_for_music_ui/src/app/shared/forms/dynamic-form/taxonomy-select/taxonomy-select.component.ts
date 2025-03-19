import { Component, forwardRef, Input, ViewChild, OnInit, OnChanges, SimpleChanges, ChangeDetectionStrategy, ChangeDetectorRef, Output, EventEmitter, OnDestroy } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';

import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { ApiService } from '../../../rest/api.service';
import { SpecificationUpdateEvent } from '../specification-update-event';
import { ApiModel } from 'app/shared/rest/api-model';
import { Subscription } from 'rxjs';



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
export class TaxonomySelectComponent implements ControlValueAccessor, OnInit, OnChanges, OnDestroy {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent

    _value: any[] = [];
    @Input() question: ApiModel;
    @Input() path: string;

    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();

    specification: any;
    specificationType: SpecificationUpdateEvent["type"];
    specificationMap: Map<number, any> = new Map<number, any>();
    @Input() specifications: any[] = [];


    displayName: string;

    searchTerm: string;

    onChange: any = () => {};

    onTouched: any = () => {};

    private sub: Subscription|null = null;

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
        let newValue: ApiObject[];
        if (val == undefined) {
            newValue = []
        } else {
            if (!this.isArray) {
                if ((val as ApiObject).id === this.nullValue.id) {
                    newValue = [];
                } else {
                    newValue = [val as ApiObject];
                }
            } else {
                newValue = [...(val as ApiObject[])];
            }
        }
        if (newValue == undefined && this._value == undefined) {
            return;
        }
        if (this._value != null && this._value.length === newValue.length) {
            if (newValue.every((v, i) => v.id === this._value[i].id)) {
                return;
            }
        }
        this._value = newValue;
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
        this.sub = this.api.getTaxonomy(this.question['x-taxonomy']).subscribe(taxonomy => {
            if (taxonomy == undefined) {
                return;
            }
            this.displayName = taxonomy.name;
            this.specificationType = taxonomy.specification;
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

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
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
        if (this.specificationType) {
            this.specificationsUpdate.emit({path: this.path + (this.isArray ? '.' + id : ''), type: this.specificationType});
        }
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

import { Component, forwardRef, Input, OnInit, ViewChild, OnDestroy, } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { Subscription, Observable } from 'rxjs/Rx';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { myDialogComponent } from '../../../dialog/dialog.component';



@Component({
  selector: 'm4m-reference-chooser',
  templateUrl: 'reference-chooser.component.html',
  styleUrls: ['reference-chooser.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => ReferenceChooserComponent),
    multi: true
  }],
})
export class ReferenceChooserComponent implements ControlValueAccessor, OnInit, OnDestroy {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    selected: any[] = [];
    @Input() question: QuestionBase<any>;

    searchTerm: string = '';

    choices: ApiObject[];
    asyncChoices: any;

    private subscription: Subscription;

    formModel: string;
    formStartData: any;
    valid: boolean;

    newData: any;

    onChange: any = () => {};

    onTouched: any = () => {};

    @Input('value')
    get value(): ApiObject|ApiObject[] {
        if (this.choices == null || this.selected == null || this.selected.length === 0) {
            if (this.question.isArray) {
                return [];
            } else {
                return this.question.nullValue;
            }
        }
        if (this.question.isArray) {
            return this.selected;
        } else {
            if (this.selected.length > 0) {
                return this.selected[0];
            } else {
                return this.question.nullValue;
            }
        }
    }

    set value(val: ApiObject|ApiObject[]) {
        if (this.question.isArray) {
            this.selected = (val as ApiObject[]);
        } else {
            if (val != null && this.question.nullValue != null
                && (val as ApiObject).id != null
                && (val as ApiObject).id === this.question.nullValue.id) {
                this.selected = [];
            } else {
                this.selected = [val];
            }
        }
        this.onChange(val);
        this.onTouched();
    }

    get placeholder(): string {
        if (this.question == null || this.question.valueType == null) {
            return '';
        }
        if (this.question.valueType == 'person') {
            return 'Person';
        }
        if (this.question.valueType == 'opus') {
            return 'Werk';
        }
        return '';
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        this.updateChoices();
        if (this.question.valueType === 'person') {
            this.formModel = 'PersonPOST';
        }
        if (this.question.valueType === 'opus') {
            this.formModel = 'OpusPOST';
        }
    }

    private updateChoices(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.question.valueType === 'person') {
            this.asyncChoices = this.api.getPeople();
            this.subscription = this.api.getPeople().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
            });
        };
        if (this.question.valueType === 'opus') {
            this.asyncChoices = this.api.getOpuses();
            this.subscription = this.api.getOpuses().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
            });
        };
    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    createNew = (data) => {
        this.newData = data;
        if (this.question.valueType === 'person') {
            data.gender = 'male';
        }
        if (this.question.valueType === 'opus') {
            data.composer = {id: -1};
        }
        this.formStartData = data;
        this.dialog.open();
    }

    selectedChange(selected: ApiObject[]) {
        this.selected = selected;
        this.dropdown.closeDropdown();
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

    save = () => {
        const updateSelection = (data) => {
            if (this.question.isArray) {
                this.selected.push(data);
            } else {
                this.selected = [data];
            }
            this.onChange(this.value);
            this.onTouched();
        }
        if (this.valid) {
            if (this.question.valueType === 'person') {
                this.api.postPerson(this.newData).take(1).subscribe(data => {
                    Observable.timer(150).take(1).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
            if (this.question.valueType === 'opus') {
                this.api.postOpus(this.newData).take(1).subscribe(data => {
                    Observable.timer(150).take(1).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
        }
    }
}

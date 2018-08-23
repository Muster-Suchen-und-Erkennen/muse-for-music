import { Component, forwardRef, Input, OnInit, ViewChild, OnDestroy, ChangeDetectorRef, ChangeDetectionStrategy } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { Subscription, Observable } from 'rxjs/Rx';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { QuestionBase } from '../../question-base';
import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { myDialogComponent } from '../../../dialog/dialog.component';
import { SelectionListComponent } from '../selection-list/slection-list.component';



@Component({
  selector: 'm4m-reference-chooser',
  templateUrl: 'reference-chooser.component.html',
  styleUrls: ['reference-chooser.component.scss'],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => ReferenceChooserComponent),
    multi: true
  }],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReferenceChooserComponent implements ControlValueAccessor, OnInit, OnDestroy {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    @ViewChild(SelectionListComponent) selectionList: SelectionListComponent;

    selected: any[] = [];
    @Input() question: QuestionBase<any>;

    searchTerm: string = '';

    choices: ApiObject[];

    private afterChoiceUpdate: () => void;

    private subscription: Subscription;

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

    constructor(private api: ApiService, private chref: ChangeDetectorRef) {}

    ngOnInit(): void {
        this.updateChoices();
    }

    private updateChoices(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.question.valueType === 'person') {
            this.subscription = this.api.getPeople().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
                if (this.afterChoiceUpdate != null) {
                    this.afterChoiceUpdate();
                }
            });
        };
        if (this.question.valueType === 'opus') {
            this.subscription = this.api.getOpuses().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
            });
        };
    }
    private refreshChoices(): void {
        if (this.question.valueType === 'person') {
            this.api.getPeople();
        };
        if (this.question.valueType === 'opus') {
            this.api.getOpuses();
        };

    }

    ngOnDestroy(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    createNew = (data) => {
        this.newData = data;
        this.dialog.open();
    }

    selectedChange(selected: ApiObject[]) {
        this.selected = selected;
        this.dropdown.closeDropdown();
        this.chref.markForCheck();
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


    formModel() {
        if (this.question.valueType === 'person') {
            return 'PersonPOST';
        }
        if (this.question.valueType === 'opus') {
            return 'OpusPOST';
        }
    }


    formStartData() {
        if (this.question.valueType === 'person') {
            return {'name': this.searchTerm, 'gender': 'male'};
        }
        if (this.question.valueType === 'opus') {
            return {'name': this.searchTerm, composer: {id: -1}};
        }
    }

    private selectNewObject(data) {

        this.afterChoiceUpdate = () => {
            Observable.timer(150).take(1).subscribe(() => {
                this.selectionList.select(data.id);
            });
            this.afterChoiceUpdate = null;
        }
        this.refreshChoices();
    }


    save = () => {
        if (this.valid) {
            if (this.question.valueType === 'person') {
                this.api.postPerson(this.newData).take(1).subscribe(data => {
                    this.selectNewObject(data);
                });
            }
            if (this.question.valueType === 'opus') {
                this.api.postOpus(this.newData).take(1).subscribe(data => {
                    this.selectNewObject(data);
                });
            }
        }
    }
}

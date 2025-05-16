
import {timer as observableTimer,  Subscription, Observable } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, forwardRef, Input, OnInit, ViewChild, OnDestroy, OnChanges, } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

import { myDropdownComponent } from '../../../dropdown/dropdown.component';
import { myDialogComponent } from '../../../dialog/dialog.component';
import { ApiModel } from 'app/shared/rest/api-model';



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
export class ReferenceChooserComponent implements ControlValueAccessor, OnInit, OnChanges, OnDestroy {

    @ViewChild(myDropdownComponent) dropdown: myDropdownComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    selected: any[] = [];
    @Input() question: ApiModel;
    @Input() path: string;
    @Input() context: any;

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

    selectableId(index, selectable) {
        return selectable.id;
    }

    @Input('value')
    get value(): ApiObject|ApiObject[] {
        const noChoices = this.choices != null && this.choices.length === 0;
        if (noChoices || this.selected == null || this.selected.length === 0) {
            return this.nullValue;
        }
        if (this.question['x-isArray']) {
            return this.selected;
        } else {
            if (this.selected.length > 0) {
                return this.selected[0];
            } else {
                return this.nullValue;
            }
        }
    }

    set value(val: ApiObject|ApiObject[]) {
        let newValue: ApiObject[];
        if (this.question['x-isArray']) {
            newValue = [...(val as ApiObject[])];
        } else {
            if (val != null && this.nullValue != null
                && (val as ApiObject).id != null
                && (val as ApiObject).id === this.nullValue.id) {
                newValue = [];
            } else {
                newValue = [val as ApiObject];
            }
        }
        if (newValue == undefined && this.selected == undefined) {
            return;
        }
        if (this.selected != null && this.selected.length === newValue.length) {
            if (newValue.every((v, i) => v.id === this.selected[i].id)) {
                return;
            }
        }
        this.selected = newValue;
        this.onChange(this.value);
        this.onTouched();
    }

    get nullValue(): any {
        if (this.question['x-isArray']) {
            return [];
        } else {
            if (this.question != null && this.question.hasOwnProperty('x-nullValue')) {
                return this.question['x-nullValue'];
            }
            return {id: -1};
        }
    }

    get isArray() {
        return this.question != null && this.question['x-isArray'];
    }

    get placeholder(): string {
        if (this.question == null || this.question['x-reference'] == null) {
            return '';
        }
        if (this.question['x-reference'] === 'person') {
            return 'Person';
        }
        if (this.question['x-reference'] === 'opus') {
            return 'Werk';
        }
        if (this.question['x-reference'] === 'voice') {
            return 'Stimme';
        }
        return '';
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        this.updateChoices();
        if (this.question['x-reference'] === 'person') {
            this.formModel = 'PersonPOST';
        }
        if (this.question['x-reference'] === 'opus') {
            this.formModel = 'OpusPOST';
        }
        if (this.question['x-reference'] === 'voice') {
            this.formModel = 'VoicePOST';
        }
    }

    ngOnChanges(changes) {
        if (changes.context != null) {
            this.updateChoices();
        }
    }

    private updateChoices(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
        if (this.question['x-reference'] === 'person') {
            this.asyncChoices = this.api.getPeople();
            this.subscription = this.api.getPeople().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
                this.onChange(this.value);
            });
        };
        if (this.question['x-reference'] === 'opus') {
            this.asyncChoices = this.api.getOpuses();
            this.subscription = this.api.getOpuses().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
                this.onChange(this.value);
            });
        };
        if (this.question['x-reference'] === 'voice') {
            if (this.context == null) {
                return; // can only load voices if context is properly setup
            }
            if (this.context.subPart != null) {
                this.asyncChoices = this.api.getVoices(this.context.subPart);
            } else if (this.context.voice != null) {
                this.asyncChoices = this.api.getVoices(this.context.voice);
            } else {
                console.log('No context provided for referencechooser!')
            }
            this.subscription = this.asyncChoices.subscribe(data => {
                if (data == undefined) {
                    return;
                }
                const choices = []
                data.forEach(voice => {
                    if (this.context.voice != null) {
                        if (this.context.voice.id === voice.id) {
                            // filter out own voice
                            return;
                        }
                    }
                    choices.push(voice);
                })
                this.choices = choices;
                this.onChange(this.value);
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
        if (this.question['x-reference'] === 'person') {
            data.gender = 'male';
        }
        if (this.question['x-reference'] === 'opus') {
            data.composer = {id: -1};
        }
        if (this.question['x-reference'] === 'voice') {
        }
        this.formStartData = data;
        this.dialog.open();
    }

    selectedChange(selected: ApiObject[]) {
        this.selected = [...selected];
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
            if (this.question['x-isArray']) {
                this.selected.push(data);
            } else {
                this.selected = [data];
            }
            this.onChange(this.value);
            this.onTouched();
        }
        if (this.valid) {
            if (this.question['x-reference'] === 'person') {
                this.api.postPerson(this.newData).pipe(take(1)).subscribe(data => {
                    observableTimer(150).pipe(take(1)).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
            if (this.question['x-reference'] === 'opus') {
                this.api.postOpus(this.newData).pipe(take(1)).subscribe(data => {
                    observableTimer(150).pipe(take(1)).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
        }
    }
}

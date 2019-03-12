import { Component, forwardRef, Input, OnInit, ViewChild, OnDestroy, } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

import { Subscription, Observable } from 'rxjs/Rx';

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
export class ReferenceChooserComponent implements ControlValueAccessor, OnInit, OnDestroy {

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
        if (this.choices == null || this.selected == null || this.selected.length === 0) {
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
        if (this.question['x-isArray']) {
            this.selected = (val as ApiObject[]);
        } else {
            if (val != null && this.nullValue != null
                && (val as ApiObject).id != null
                && (val as ApiObject).id === this.nullValue.id) {
                this.selected = [];
            } else {
                this.selected = [val];
            }
        }
        this.onChange(val);
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
            });
        };
        if (this.question['x-reference'] === 'opus') {
            this.asyncChoices = this.api.getOpuses();
            this.subscription = this.api.getOpuses().subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.choices = data;
            });
        };
        if (this.question['x-reference'] === 'voice') {
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
                this.api.postPerson(this.newData).take(1).subscribe(data => {
                    Observable.timer(150).take(1).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
            if (this.question['x-reference'] === 'opus') {
                this.api.postOpus(this.newData).take(1).subscribe(data => {
                    Observable.timer(150).take(1).subscribe(() => {
                        updateSelection(data);
                    });
                });
            }
        }
    }
}

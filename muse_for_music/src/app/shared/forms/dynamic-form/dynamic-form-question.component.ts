import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';

@Component({
    selector: 'df-question',
    templateUrl: './dynamic-form-question.component.html'
})
export class DynamicFormQuestionComponent {

    @Input() question: QuestionBase<any>;
    @Input() form: FormGroup;
    @Input() path: string;
    @Input() nested: boolean = false;

    @Input() specificationsCallback: (path: string, remove: boolean, recursive: boolean, affectsArrayMembers: boolean) => void;

    questionSpec;
    _specifications = [];
    @Input()
    set specifications(specifications: any[]) {
        this._specifications = specifications;
        specifications.forEach((spec) => {
            if (spec.path === this.path) {
                this.questionSpec = spec;
            }
        })
    }

    get specifications() {
        return this._specifications;
    }

    @Output() opened = new EventEmitter();

    open: boolean = false;

    isCollapsible() {
        if (this.question == null || this.question.nestedQuestions == null) {
            return false;
        }
        return this.question.nestedQuestions.filter(qstn => !qstn.readOnly).length > 2;
    }

    toggleOpen() {
        if (this.question != null && this.question.controlType === 'object' &&
            this.question.nestedQuestions != null && this.question.nestedQuestions.length > 2) {
            if (! this.open) {
                this.opened.emit(this.question.key);
            }
            this.open = !this.open;
        }
    }

    close(sourceKey: string) {
        if (this.question != null && this.question.key == sourceKey) {
            return;
        }
        this.open = false;
    }

    get isValid() { return this.form.controls[this.question.key].valid; }

    get error() {
        if (this.form.controls[this.question.key].valid) {
            return '';
        }
        const errors = this.form.controls[this.question.key].errors;
        if (errors) {
            if (errors.maxlength) {
                return 'Nur '  + errors.maxlength.requiredLength + ' Zeichen erlaubt.';
            }
            if (errors.pattern) {
                return 'Der Eingegebene Text hat nicht das erwartete Format.'
            }
            if (errors.required) {
                return 'Dieses Feld muss noch ausgefüllt werden.';
            }
            if (errors.null) {
                return 'Dieses Feld muss noch ausgefüllt werden.';
            }
            console.log(errors);
        }
        return 'Überprüfen sie bitte die Eingabe.';
    }
}

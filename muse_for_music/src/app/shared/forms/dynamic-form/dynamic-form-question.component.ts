import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';

@Component({
    selector: 'df-question',
    templateUrl: './dynamic-form-question.component.html'
})
export class DynamicFormQuestionComponent {

    @Input() question: QuestionBase<any>;
    @Input() form: FormGroup;
    @Input() nested: boolean = false;

    open: boolean = false;

    get isValid() { return this.form.controls[this.question.key].valid; }

    get error() {
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

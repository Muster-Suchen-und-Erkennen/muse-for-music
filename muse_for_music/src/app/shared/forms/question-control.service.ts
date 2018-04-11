import { Injectable } from '@angular/core';
import { FormControl, FormGroup, FormArray, Validators } from '@angular/forms';
import { Observable } from 'rxjs/Rx';

import { QuestionBase } from './question-base';
import { QuestionService } from './question.service';

@Injectable()
export class QuestionControlService {
    constructor(private qstn: QuestionService) { }

    toFormGroup(questions: QuestionBase<any>[]): Observable<FormGroup> {
        return Observable.from(questions).concatMap(question => {
            const formControl = {
                key: question.key,
                question: question,
                control: null,
            }

            if (question.controlType === 'array') {
                formControl.control = new FormArray([]);
                return Observable.of(formControl);
            }
            if (question.controlType === 'object') {
                return this.qstn.getQuestions(question.valueType).flatMap(questions => this.toFormGroup(questions)).map(control => {
                    formControl.control = control;
                    return formControl;
                });
            }

            const validators = [];
            if (question.required) {
                if (question.controlType === 'boolean') {
                    // nothing
                } else if (question.controlType === 'string' || question.controlType === 'text') {
                    if (question.min != null && question.min === 1) {
                        validators.push(Validators.required);
                    }
                    if (question.pattern != null) {
                        validators.push(Validators.pattern(question.pattern));
                    }
                } else {
                    validators.push(Validators.required);
                }
            }
            if (question.min != undefined) {
                if (question.controlType === 'number') {
                    validators.push(Validators.min(question.min as number));
                }
                if (question.controlType === 'string' || question.controlType === 'text') {
                    if (question.min > 1) {
                        validators.push(Validators.minLength(question.min as number))
                    }
                }
            }
            if (question.max != undefined) {
                if (question.controlType === 'number') {
                    validators.push(Validators.max(question.max as number));
                }
                if (question.controlType === 'string' || question.controlType === 'text') {
                    validators.push(Validators.maxLength(question.max as number))
                }
            }

            if (validators.length > 1) {
                const validator = Validators.compose(validators);
                formControl.control = new FormControl(question.value || '', validator)
            } else if (validators.length === 1) {
                formControl.control = new FormControl(question.value || '', validators[0])
            } else {
                formControl.control = new FormControl(question.value || '');
            }
            return Observable.of(formControl);
        }).reduce((group: {[propName: string]: any}, formControl: {key: string, control: any}) => {
            group[formControl.key] = formControl.control;
            return group;
        }, {}).map(group => new FormGroup(group));
    }
}

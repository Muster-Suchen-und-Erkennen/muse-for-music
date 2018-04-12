import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';
import { patch } from 'webdriver-js-extender';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    questions: QuestionBase<any>[] = [];
    form: FormGroup;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;

    constructor(private qcs: QuestionControlService, private qs: QuestionService) { }

    closeUnrelated(sourceKey) {
        this.questionDivs.forEach(question => question.close(sourceKey));
    }

    update() {
        this.qs.getQuestions(this.objectModel).subscribe(questions => {
            this.questions = questions;

            this.qcs.toFormGroup(this.questions).subscribe(form => {
                this.form = form;
                this.form.statusChanges.subscribe(status => {
                    this.valid.emit(this.form.valid);
                    this.data.emit(this.form.value);
                });
                this.patchFormValues();
            });
        });
    }

    patchFormValues() {
        if (this.form != null) {
            const patched = {};
            const patch = (values, questions, patched) => {
                questions.forEach(question => {
                    if (question.controlType === 'object') {
                        const next = {};
                        patched[question.key] = next;
                        patch(values[question.key], question.nestedQuestions, next);
                        return;
                    }
                    if (values != null && values[question.key] != null) {
                        patched[question.key] = values[question.key];
                    } else {
                        patched[question.key] = question.nullValue;
                    }
                });
            }
            patch(this.startValues, this.questions, patched);
            this.form.patchValue(patched);
        }
    }

    ngOnInit() {
        this.update();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.objectType != null) {
            this.update();
        } else {
            if (this.form != null && changes.startValues != null) {
                this.patchFormValues();
            }
        }
    }
}

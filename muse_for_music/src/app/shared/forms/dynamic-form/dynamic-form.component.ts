import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { Subscription } from 'rxjs/Rx';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';
import { SaveButtonComponent } from './save-button/save-button.component';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    @Input() showSaveButton: boolean = false;
    @Input() saveSuccess: boolean = false;

    questions: QuestionBase<any>[] = [];
    form: FormGroup;
    valueChangeSubscription: Subscription;

    private canSave: boolean;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() validForSave: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;
    @ViewChild(SaveButtonComponent) savebutton: SaveButtonComponent;

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
                    if (this.form.valid) {
                        this.validForSave.emit(true);
                        this.canSave = true;
                    } else {
                        let valid = true;
                        this.questions.forEach(qstn => {
                            if (!qstn.allowSave) {
                                if (!this.form.controls[qstn.key].valid) {
                                    valid = false;
                                }
                            }
                        });
                        this.canSave = valid;
                        this.validForSave.emit(valid);
                    }
                });
                this.patchFormValues();
            });
        });
    }

    patchFormValues = () => {
        if (this.form != null) {
            const patched = {};
            const patchValues = (values, questions, patched) => {
                questions.forEach((question: QuestionBase<any>) => {
                    if (question.controlType === 'object') {
                        const next = {};
                        patched[question.key] = next;
                        patchValues(values != null ? values[question.key] : undefined,
                                    question.nestedQuestions, next);
                        return;
                    }
                    if (values != null && values[question.key] != null) {
                        patched[question.key] = values[question.key];
                    } else {
                        if (question.isArray) {
                            patched[question.key] = [];
                        } else {
                            if (question.value != null) {
                                patched[question.key] = question.value;
                            } else {
                                patched[question.key] = question.nullValue;
                            }
                        }
                    }
                });
            }
            patchValues(this.startValues, this.questions, patched);
            if (this.valueChangeSubscription != null) {
                this.valueChangeSubscription.unsubscribe();
            }
            this.form.patchValue(patched);
            this.valueChangeSubscription = this.form.valueChanges.take(1).subscribe(() => {
                if (this.savebutton != null) {
                    this.savebutton.resetStatus();
                }
            });
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

    saveForm = () => {
        if (this.form != null && this.canSave) {
            this.save.emit(this.form.value);
        }
    }

    saveFinished = (success: boolean) => {
        if (this.savebutton != null) {
            this.savebutton.saveFinished(success);
        }
    }
}

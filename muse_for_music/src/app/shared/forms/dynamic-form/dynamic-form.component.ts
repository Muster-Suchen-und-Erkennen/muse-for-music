import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild } from '@angular/core';
import { FormGroup, FormArray } from '@angular/forms';

import { Subscription } from 'rxjs/Rx';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';
import { SaveButtonComponent } from './save-button/save-button.component';
import { myDialogComponent } from '../../dialog/dialog.component';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    @Input() showSaveButton: boolean = false;
    @Input() alwaysAllowSave: boolean = false;
    @Input() saveSuccess: boolean = false;

    questions: QuestionBase<any>[] = [];
    form: FormGroup;
    valueChangeSubscription: Subscription;

    specifications: {path: string, share: ApiObject, occurence: ApiObject, instrumentation: ApiObject[]}[] = [];
    currentSpec: {path: string, share: ApiObject, occurence: ApiObject, instrumentation: ApiObject[]};

    private canSave: boolean;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() validForSave: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;
    @ViewChild(SaveButtonComponent) savebutton: SaveButtonComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    constructor(private qcs: QuestionControlService, private qs: QuestionService) { }

    questionId(index, qstn: QuestionBase<any>) {
        return qstn.key;
    }

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
            const patchArrays = (patched, questions, path) => {
                questions.forEach(question => {
                    if (question.controlType === 'object') {
                        const newpath = path.length > 0 ? path + '.' + question.key : question.key
                        patchArrays(patched[question.key], question.nestedQuestions, newpath);
                        return;
                    }
                    if (question.isArray || question.controlType === 'array') {
                        if (question.type !== 'taxonomy' && question.type !== 'reference') {
                            const newpath = path.length > 0 ? path + '.' + question.key : question.key
                            const arrayControl: FormArray = this.form.get(newpath) as FormArray;
                            let counter = 0;
                            while (arrayControl.length !== patched[question.key].length) {
                                counter ++;
                                if (counter > 100000) {
                                    break; // don't allow infinite loops
                                }
                                if (arrayControl.length < patched[question.key].length) {
                                    this.qs.getQuestions(question.valueType).take(1).subscribe((questions => {
                                        this.qcs.toFormGroup(questions).take(1).subscribe((group => {
                                            arrayControl.push(group);
                                        }));
                                    }));
                                }
                                if (arrayControl.length > patched[question.key].length) {
                                    arrayControl.removeAt(arrayControl.length - 1);
                                }
                            }
                        }
                    }
                });
            }
            patchArrays(patched, this.questions, '')
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

    updateSpecification = (path: string, remove: boolean = false, recursive: boolean = false, affectsArrayMembers: boolean = false) => {
        if (remove) {
            const newSpecifications = [];
            this.specifications.forEach((spec) => {
                if (recursive) {
                    if (spec.path !== path && !spec.path.startsWith(path + '.')) {
                        newSpecifications.push(spec);
                    }
                } else {
                    if (spec.path !== path) {
                        newSpecifications.push(spec);
                    }
                }
                if (affectsArrayMembers) {
                    const splitpath = path.split('.');
                    const splitpathSpec = spec.path.split('.');
                    const arrayIndex = parseInt(splitpath[splitpath.length - 1], 10);
                    const arrayIndexSpec = parseInt(splitpathSpec[splitpath.length - 1], 10);
                    if (arrayIndex < arrayIndexSpec) {
                        splitpathSpec[splitpath.length - 1] = '' + (arrayIndexSpec - 1);
                    }
                    spec.path = splitpathSpec.join('.');
                }
            });
            this.specifications = newSpecifications;
        } else {
            this.currentSpec = null;
            this.specifications.forEach((spec) => {
                if (spec.path === path) {
                    this.currentSpec = spec;
                }
            });
            if (this.currentSpec == null) {
                this.currentSpec = {
                    path: path,
                    share: {id: -1, _links: {self: {href: ''}}},
                    occurence: {id: -1, _links: {self: {href: ''}}},
                    instrumentation: [],
                }
            }
            this.dialog.open();
        }
    }

    saveSpec = () => {
        const newSpecifications = [];
        this.specifications.forEach((spec) => {
            if (spec.path === this.currentSpec.path) {
                newSpecifications.push(this.currentSpec);
                this.currentSpec = null;
            } else {
                newSpecifications.push(spec);
            }
        });
        if (this.currentSpec != null) {
            newSpecifications.push(this.currentSpec);
        }
        this.specifications = newSpecifications;
    }

    saveForm = () => {
        if (this.form != null && (this.canSave || this.alwaysAllowSave)) {
            this.save.emit(this.form.value);
        }
    }

    saveFinished = (success: boolean) => {
        if (this.savebutton != null) {
            this.savebutton.saveFinished(success);
        }
    }
}

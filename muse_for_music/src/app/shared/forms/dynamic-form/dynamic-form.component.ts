import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    questions: QuestionBase<any>[] = [];
    customNull: {[propName: string]: any} = {};
    conversions: {[propName: string]: string} = {};
    form: FormGroup;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    constructor(private qcs: QuestionControlService, private qs: QuestionService) { }

    update() {
        this.qs.getQuestions(this.objectModel).subscribe(questions => {
            this.questions = questions;
            this.customNull = {};
            this.conversions = {};

            function recursiveParse(questions, customNull, conversions, qs) {
                for (let question of questions) {
                    if (question.nullValue != undefined) {
                        customNull[question.key] = question.nullValue;
                    }
                    if (question.valueType === 'integer') {
                        conversions[question.key] = question.valueType;
                    }
                    if (question.controlType === 'object') {
                        const temp1 = {$continuation:true};
                        const temp2 = {$continuation:true};
                        customNull[question.key] = temp1;
                        conversions[question.key] = temp2;
                        qs.getQuestions(question.valueType).subscribe(questions => recursiveParse(questions, temp1, temp2, qs))
                    }
                }
            }
            recursiveParse(questions, this.customNull, this.conversions, this.qs);

            this.qcs.toFormGroup(this.questions).subscribe(form => {
                this.form = form;
                this.form.statusChanges.subscribe(status => {
                    this.valid.emit(this.form.valid);
                    let patched = {};

                    function recursivePatchNulls(value, patched, customNull) {
                        for (let key in value) {
                            if (customNull[key] != null && customNull[key]['$continuation']) {
                                patched[key] = {};
                                recursivePatchNulls(value[key], patched[key], customNull[key]);
                            } else if (value[key] != null && value[key] != '') {
                                patched[key] = value[key];
                            } else {
                                patched[key] = customNull[key];
                            }
                        }
                    }

                    recursivePatchNulls(this.form.value, patched, this.customNull);

                    function recursivePatchConversions(patched, conversions) {
                        for (let key in patched) {
                            if (conversions[key] != null && conversions[key]['$continuation']) {
                                recursivePatchConversions(patched[key], conversions[key]);
                            } else if (conversions[key] === 'integer') {
                                patched[key] = parseInt(patched[key], 10);
                            }
                        }
                    }

                    recursivePatchConversions(patched, this.conversions);

                    this.data.emit(patched);
                });
                this.patchFormValues();
            });
        });
    }

    patchFormValues() {
        let patched = {};

        function recursivePatch(values, patched, customNull) {
            for (let key in values) {
                if (customNull[key] != null && customNull[key]['$continuation']) {
                    patched[key] = {};
                    recursivePatch(values[key], patched[key], customNull[key]);
                } else if (customNull[key] !== values[key]) {
                    patched[key] = values[key];
                } else {
                    patched[key] = null;
                }
            }
        }

        recursivePatch(this.startValues, patched, this.customNull);

        if (this.form != undefined) {
            this.form.patchValue(patched);
        }
    }

    ngOnInit() {
        this.update();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.objectType != undefined) {
            this.update();
        } else {
            if (this.form != undefined && changes.startValues != undefined) {
                this.patchFormValues();
            }
        }
    }
}

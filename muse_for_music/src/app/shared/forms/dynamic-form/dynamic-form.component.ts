import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../../rest/api-base.service';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService]
})
export class DynamicFormComponent implements OnInit, OnChanges {

    @Input() objectType: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};

    questions: QuestionBase<any>[] = [];
    form: FormGroup;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    constructor(private qcs: QuestionControlService, private qs: QuestionService) { }

    update() {
        this.questions = this.qs.getQuestions();
        this.form = this.qcs.toFormGroup(this.questions);
        this.form.statusChanges.subscribe(status => {
            this.valid.emit(this.form.valid);
            this.data.emit(this.form.value);
        });
    }

    ngOnInit() {
        this.update();
        this.form.patchValue(this.startValues);
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.objectType != undefined) {
            this.update();
        }
        if (changes.startValues != undefined) {
            this.form.patchValue(this.startValues);
        }
    }
}
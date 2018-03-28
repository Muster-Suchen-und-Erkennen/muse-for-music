import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { FormArray } from '@angular/forms';

import { QuestionBase } from '../../question-base';
import { QuestionService } from '../../question.service';
import { QuestionControlService } from '../../question-control.service';



@Component({
  selector: 'm4m-array-input',
  templateUrl: 'array-input.component.html',
  styleUrls: ['array-input.component.scss'],
})
export class ArrayInputComponent {

    @Input() question: QuestionBase<any>;
    @Input() array: FormArray;

    constructor (private qcs: QuestionControlService, private qs: QuestionService) {}

    newItem() {
        this.qs.getQuestions(this.question.valueType).take(1).subscribe((questions => {
            this.qcs.toFormGroup(questions).take(1).subscribe((group => {
                this.array.push(group);
            }).bind(this));
        }).bind(this));
    }

    deleteItem(i) {
        this.array.removeAt(i);
    }

}

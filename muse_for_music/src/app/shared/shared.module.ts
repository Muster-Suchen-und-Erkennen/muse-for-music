import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicFormComponent }         from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormQuestionComponent } from './forms/dynamic-form/dynamic-form-question.component';

import { QuestionControlService } from './forms/question-control.service';
import { QuestionService } from './forms/question.service';


import { myBoxComponent } from './box/box.component';

@NgModule({
    imports:      [ CommonModule, FormsModule, ReactiveFormsModule ],
    declarations: [ myBoxComponent, DynamicFormComponent, DynamicFormQuestionComponent ],
    providers: [
        QuestionService,
        QuestionControlService,
    ],
    exports: [
        myBoxComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,

        CommonModule,
        FormsModule,
        ReactiveFormsModule
    ]
})
export class SharedModule { }

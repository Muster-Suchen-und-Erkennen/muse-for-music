import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicFormComponent } from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormQuestionComponent } from './forms/dynamic-form/dynamic-form-question.component';
import { ReferenceChooserComponent } from './forms/dynamic-form/reference-chooser/reference-chooser.component';

import { QuestionControlService } from './forms/question-control.service';
import { QuestionService } from './forms/question.service';
import { BaseApiService } from './rest/api-base.service';
import { ApiService } from './rest/api.service';


import { myBoxComponent } from './box/box.component';

@NgModule({
    imports:      [ CommonModule, FormsModule, ReactiveFormsModule ],
    declarations: [ myBoxComponent, DynamicFormComponent, DynamicFormQuestionComponent, ReferenceChooserComponent, ],
    providers: [
        QuestionService,
        QuestionControlService,
        ApiService,
        BaseApiService,
    ],
    exports: [
        myBoxComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,
        ReferenceChooserComponent,

        CommonModule,
        FormsModule,
        ReactiveFormsModule
    ]
})
export class SharedModule { }

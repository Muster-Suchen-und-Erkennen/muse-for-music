import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicFormComponent } from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormQuestionComponent } from './forms/dynamic-form/dynamic-form-question.component';
import { ReferenceChooserComponent } from './forms/dynamic-form/reference-chooser/reference-chooser.component';
import { SelectionListComponent } from './forms/dynamic-form/selection-list/slection-list.component';
import { TaxonomySelectComponent } from './forms/dynamic-form/taxonomy-select/taxonomy-select.component';
import { TaxonomySelectionListComponent } from './forms/dynamic-form/taxonomy-selection-list/taxonomy-slection-list.component';

import { QuestionControlService } from './forms/question-control.service';
import { QuestionService } from './forms/question.service';
import { BaseApiService } from './rest/api-base.service';
import { ApiService } from './rest/api.service';


import { myBoxComponent } from './box/box.component';
import { myDropdownComponent } from './dropdown/dropdown.component';

import { ClickOutsideDirective } from './click-outside.directive';

@NgModule({
    imports:      [ CommonModule, FormsModule, ReactiveFormsModule ],
    declarations: [
        myBoxComponent,
        myDropdownComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,
        ReferenceChooserComponent,
        SelectionListComponent,
        TaxonomySelectComponent,
        TaxonomySelectionListComponent,
        ClickOutsideDirective,
    ],
    providers: [
        QuestionService,
        QuestionControlService,
        ApiService,
        BaseApiService,
    ],
    exports: [
        myBoxComponent,
        myDropdownComponent,
        DynamicFormComponent,
        DynamicFormQuestionComponent,
        ReferenceChooserComponent,
        SelectionListComponent,
        TaxonomySelectComponent,
        TaxonomySelectionListComponent,
        ClickOutsideDirective,

        CommonModule,
        FormsModule,
        ReactiveFormsModule
    ]
})
export class SharedModule { }

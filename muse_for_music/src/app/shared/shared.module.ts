import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicDataComponent } from './data/dynamic-data/dynamic-data.component';
import { DataItemComponent } from './data/data-item/data-item.component';
import { DataReferenceComponent } from './data/data-reference/data-reference.component';
import { DataArrayComponent } from './data/data-array/data-array.component';
import { DataTaxonomyComponent } from './data/data-taxonomy/data-taxonomy.component';

import { DynamicFormComponent } from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormQuestionComponent } from './forms/dynamic-form/dynamic-form-question.component';
import { SaveButtonComponent } from './forms/dynamic-form/save-button/save-button.component';
import { NumberInputComponent } from './forms/dynamic-form/number-input/number-input.component';
import { BooleanInputComponent } from './forms/dynamic-form/boolean-input/boolean-input.component';
import { DateInputComponent } from './forms/dynamic-form/date-input/date-input.component';
import { ArrayInputComponent } from './forms/dynamic-form/array-input/array-input.component';
import { ReferenceChooserComponent } from './forms/dynamic-form/reference-chooser/reference-chooser.component';
import { SelectionListComponent } from './forms/dynamic-form/selection-list/slection-list.component';
import { TaxonomySelectComponent } from './forms/dynamic-form/taxonomy-select/taxonomy-select.component';
import { TaxonomySelectionListComponent } from './forms/dynamic-form/taxonomy-selection-list/taxonomy-slection-list.component';

import { QuestionControlService } from './forms/question-control.service';
import { QuestionService } from './forms/question.service';
import { BaseApiService } from './rest/api-base.service';
import { ApiService } from './rest/api.service';
import { ModelsService } from './rest/models.service';
import { UserApiService } from './rest/user-api.service';
import { LoginGuard } from './rest/login.guard';
import { AdminGuard } from './rest/admin.guard';
import { TaxonomyEditorGuard } from './rest/taxonomy-editor.guard';


import { InfoComponent } from './info/info.component';
import { InfoService } from './info/info.service';


import { myBoxComponent } from './box/box.component';
import { myDialogComponent } from './dialog/dialog.component'
import { myDropdownComponent } from './dropdown/dropdown.component';
import { myTableComponent } from './table/table.component';

import { ClickOutsideDirective } from './click-outside.directive';

@NgModule({
    imports:      [ CommonModule, FormsModule, ReactiveFormsModule ],
    declarations: [
        InfoComponent,
        myBoxComponent,
        myDialogComponent,
        myDropdownComponent,
        myTableComponent,

        DynamicDataComponent,
        DataItemComponent,
        DataReferenceComponent,
        DataArrayComponent,
        DataTaxonomyComponent,

        DynamicFormComponent,
        DynamicFormQuestionComponent,
        SaveButtonComponent,
        NumberInputComponent,
        BooleanInputComponent,
        DateInputComponent,
        ArrayInputComponent,
        ReferenceChooserComponent,
        SelectionListComponent,
        TaxonomySelectComponent,
        TaxonomySelectionListComponent,
        ClickOutsideDirective,
    ],
    providers: [
        InfoService,
        QuestionService,
        QuestionControlService,
        BaseApiService,
        ApiService,
        ModelsService,
        UserApiService,
        LoginGuard,
        AdminGuard,
        TaxonomyEditorGuard,
    ],
    exports: [
        InfoComponent,
        myBoxComponent,
        myDialogComponent,
        myDropdownComponent,
        myTableComponent,

        DynamicDataComponent,
        DataItemComponent,
        DataReferenceComponent,
        DataArrayComponent,
        DataTaxonomyComponent,

        DynamicFormComponent,
        DynamicFormQuestionComponent,
        SaveButtonComponent,
        NumberInputComponent,
        BooleanInputComponent,
        DateInputComponent,
        ArrayInputComponent,
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

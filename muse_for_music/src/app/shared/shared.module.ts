import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DynamicDataComponent } from './data/dynamic-data/dynamic-data.component';
import { DataItemComponent } from './data/data-item/data-item.component';
import { DataReferenceComponent } from './data/data-reference/data-reference.component';
import { DataArrayComponent } from './data/data-array/data-array.component';
import { DataTaxonomyComponent } from './data/data-taxonomy/data-taxonomy.component';

import { DynamicFormComponent } from './forms/dynamic-form/dynamic-form.component';
import { DynamicFormLayerComponent } from './forms/dynamic-form/dynamic-form-layer.component';
import { DynamicFormItemComponent } from './forms/dynamic-form/form-item/form-item.component';
import { SaveButtonComponent } from './forms/dynamic-form/save-button/save-button.component';
import { ObjectInputComponent } from './forms/dynamic-form/object-input/object-input.component';
import { NumberInputComponent } from './forms/dynamic-form/number-input/number-input.component';
import { BooleanInputComponent } from './forms/dynamic-form/boolean-input/boolean-input.component';
import { ArrayInputComponent } from './forms/dynamic-form/array-input/array-input.component';
import { ReferenceChooserComponent } from './forms/dynamic-form/reference-chooser/reference-chooser.component';
import { SelectionListComponent } from './forms/dynamic-form/selection-list/slection-list.component';
import { TaxonomySelectComponent } from './forms/dynamic-form/taxonomy-select/taxonomy-select.component';
import { TaxonomySelectionListComponent } from './forms/dynamic-form/taxonomy-selection-list/taxonomy-slection-list.component';

import { FormGroupService } from './forms/form-group.service';

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
        DynamicFormLayerComponent,
        DynamicFormItemComponent,
        SaveButtonComponent,
        ObjectInputComponent,
        NumberInputComponent,
        BooleanInputComponent,
        ArrayInputComponent,
        ReferenceChooserComponent,
        SelectionListComponent,
        TaxonomySelectComponent,
        TaxonomySelectionListComponent,
        ClickOutsideDirective,
    ],
    providers: [
        InfoService,
        FormGroupService,
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
        DynamicFormLayerComponent,
        DynamicFormItemComponent,
        SaveButtonComponent,
        ObjectInputComponent,
        NumberInputComponent,
        BooleanInputComponent,
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

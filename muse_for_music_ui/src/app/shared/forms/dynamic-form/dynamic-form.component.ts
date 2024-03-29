import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { FormGroup, FormArray } from '@angular/forms';

import { Subscription } from 'rxjs';

import { ApiObject } from '../../rest/api-base.service';
import { SaveButtonComponent } from './save-button/save-button.component';
import { myDialogComponent } from '../../dialog/dialog.component';
import { Specification } from './specifications';
import { SpecificationUpdateEvent } from './specification-update-event';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DynamicFormComponent implements OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};
    @Input() context: any;

    @Input() showSaveButton: boolean = false;
    @Input() alwaysAllowSave: boolean = false;
    @Input() saveSuccess: boolean = false;
    @Input() useSpecifications: boolean = true;

    @Input() debug: boolean = false;

    specifications: Specification[] = [];
    currentSpec: Specification;
    currentSpecUpdated: Specification;
    currentSpecType: SpecificationUpdateEvent["type"];

    get specModelUrl(): string {
        if (this.currentSpecType === "aa") {
            return "SpecificationAA";
        } else if (this.currentSpecType === "aai") {
            return "SpecificationAAI";
        } else {
            return "";
        }
    }

    canSave: boolean;
    formValue: any;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;
    @ViewChild(SaveButtonComponent) savebutton: SaveButtonComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    constructor(private changeDetector: ChangeDetectorRef) { }

    runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.startValues != null) {
            const newSpecifications = changes.startValues.currentValue?.specifications;
            if (newSpecifications != null) {
                this.specifications = newSpecifications;
            }
        }
        if (changes.objectModel != null || changes.startValues != null ||
            changes.context != null || changes.showSaveButton != null ||
            changes.alwaysAllowSave != null || changes.saveSuccess != null) {
            this.runChangeDetection();
        }
    }

    updateData(data) {
        if (this.useSpecifications) {
            data.specifications = this.specifications.map(spec => ({
                instrumentation: [],
                ...spec
            }));
        }
        this.formValue = data;
        Promise.resolve().then(() => this.data.emit(data));
    }

    updateValid(valid: boolean|null) {
        Promise.resolve().then(() => this.valid.emit(valid));
    }

    updateSpecification(event: SpecificationUpdateEvent) {
        if (event.remove) {
            const newSpecifications = [];
            this.specifications.forEach((spec) => {
                if (event.recursive) {
                    if (spec.path !== event.path && !spec.path.startsWith(event.path + '.')) {
                        newSpecifications.push(spec);
                    }
                } else {
                    if (spec.path !== event.path) {
                        newSpecifications.push(spec);
                    }
                }
                if (event.affectsArrayMembers) {
                    const splitpath = event.path.split('.');
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
            this.currentSpecUpdated = null;
            this.currentSpecType = event.type;
            this.specifications.forEach((spec) => {
                if (spec.path === event.path) {
                    this.currentSpec = spec;
                }
            });
            if (this.currentSpec == null) {
                this.currentSpec = {
                    path: event.path,
                    share: {id: -1, _links: {self: {href: ''}}},
                    occurence: {id: -1, _links: {self: {href: ''}}},
                    instrumentation: [],
                }
            }
            if (this.useSpecifications) {
                Promise.resolve().then(() => this.dialog.open());
            }
        }
    }

    saveSpec = () => {
        const currentSpec = this.currentSpecUpdated ?? this.currentSpec;
        const newSpecifications = [];
        this.specifications.forEach((spec) => {
            if (spec.path === currentSpec.path) {
                newSpecifications.push(currentSpec);
                this.currentSpec = null;
                this.currentSpecUpdated = null;
            } else {
                newSpecifications.push(spec);
            }
        });
        if (currentSpec != null) {
            newSpecifications.push(currentSpec);
        }
        this.specifications = newSpecifications;
    }

    cancelSpecUpdate = () => {
        this.currentSpec = null;
        this.currentSpecUpdated = null;
    }

    saveForm = () => {
        if (this.canSave || this.alwaysAllowSave) {
            this.save.emit(this.formValue);
        }
    }

    saveFinished = (success: boolean) => {
        if (this.savebutton != null) {
            this.savebutton.saveFinished(success);
        }
    }

    updateSpecData(data) {
        if (data !== this.currentSpecUpdated) {
            this.currentSpecUpdated = data
        }
    }
}

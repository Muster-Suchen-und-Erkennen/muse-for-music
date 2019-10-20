import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { FormGroup, FormArray } from '@angular/forms';

import { Subscription } from 'rxjs/Rx';

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
    @Input() useSpecifications: boolean = false;

    @Input() debug: boolean = false;

    specifications: Specification[] = [];
    currentSpec: Specification;

    canSave: boolean;
    formValue: any;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;
    @ViewChild(SaveButtonComponent) savebutton: SaveButtonComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    constructor(private changeDetector: ChangeDetectorRef) { }

    private runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.objectModel != null || changes.startValues != null ||
            changes.context != null || changes.showSaveButton != null ||
            changes.alwaysAllowSave != null || changes.saveSuccess != null) {
            this.runChangeDetection();
        }
    }

    updateData(data) {
        if (this.useSpecifications) {
            data.specifications = this.specifications;
        }
        this.formValue = data;
        this.data.emit(data);
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
                this.dialog.open();
            }
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
        if (this.canSave || this.alwaysAllowSave) {
            this.save.emit(this.formValue);
        }
    }

    saveFinished = (success: boolean) => {
        if (this.savebutton != null) {
            this.savebutton.saveFinished(success);
        }
    }
}

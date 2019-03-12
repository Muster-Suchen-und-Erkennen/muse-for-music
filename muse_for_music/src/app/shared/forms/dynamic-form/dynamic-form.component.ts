import { Component, Input, Output, OnInit, OnChanges, SimpleChanges, EventEmitter, ViewChildren, ViewChild, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { FormGroup, FormArray } from '@angular/forms';

import { Subscription } from 'rxjs/Rx';

import { QuestionBase } from '../question-base';
import { QuestionService } from '../question.service';
import { QuestionControlService } from '../question-control.service';

import { ApiObject } from '../../rest/api-base.service';
import { SaveButtonComponent } from './save-button/save-button.component';
import { myDialogComponent } from '../../dialog/dialog.component';

@Component({
    selector: 'dynamic-form',
    templateUrl: './dynamic-form.component.html',
    providers: [QuestionControlService],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DynamicFormComponent implements OnChanges {

    @Input() objectModel: string;
    @Input() startValues: ApiObject = {_links:{self:{href:''}}};
    @Input() context: any;

    @Input() showSaveButton: boolean = false;
    @Input() alwaysAllowSave: boolean = false;
    @Input() saveSuccess: boolean = false;

    questions: QuestionBase<any>[] = [];
    form: FormGroup;
    valueChangeSubscription: Subscription;

    specifications: {path: string, share: ApiObject, occurence: ApiObject, instrumentation: ApiObject[]}[] = [];
    currentSpec: {path: string, share: ApiObject, occurence: ApiObject, instrumentation: ApiObject[]};

    private canSave: boolean;

    @Output() valid: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() validForSave: EventEmitter<boolean> = new EventEmitter<boolean>();
    @Output() data: EventEmitter<any> = new EventEmitter<any>();

    @Output() save: EventEmitter<any> = new EventEmitter<any>();

    @ViewChildren('questions') questionDivs;
    @ViewChild(SaveButtonComponent) savebutton: SaveButtonComponent;

    @ViewChild(myDialogComponent) dialog: myDialogComponent;

    constructor(private qcs: QuestionControlService, private qs: QuestionService, private changeDetector: ChangeDetectorRef) { }

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

    updateSpecification = (path: string, remove: boolean = false, recursive: boolean = false, affectsArrayMembers: boolean = false) => {
        if (remove) {
            const newSpecifications = [];
            this.specifications.forEach((spec) => {
                if (recursive) {
                    if (spec.path !== path && !spec.path.startsWith(path + '.')) {
                        newSpecifications.push(spec);
                    }
                } else {
                    if (spec.path !== path) {
                        newSpecifications.push(spec);
                    }
                }
                if (affectsArrayMembers) {
                    const splitpath = path.split('.');
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
                if (spec.path === path) {
                    this.currentSpec = spec;
                }
            });
            if (this.currentSpec == null) {
                this.currentSpec = {
                    path: path,
                    share: {id: -1, _links: {self: {href: ''}}},
                    occurence: {id: -1, _links: {self: {href: ''}}},
                    instrumentation: [],
                }
            }
            this.dialog.open();
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
        if (this.form != null && (this.canSave || this.alwaysAllowSave)) {
            this.save.emit(this.form.value);
        }
    }

    saveFinished = (success: boolean) => {
        if (this.savebutton != null) {
            this.savebutton.saveFinished(success);
        }
    }
}

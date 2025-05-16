import { Component, Input, OnChanges, ChangeDetectorRef, ChangeDetectionStrategy, Output, EventEmitter, OnDestroy } from '@angular/core';
import { ApiModel, ApiModelRef } from 'app/shared/rest/api-model';
import { ModelsService } from 'app/shared/rest/models.service';
import { UntypedFormGroup } from '@angular/forms';
import { Subscription } from 'rxjs';
import { SpecificationUpdateEvent } from '../specification-update-event';

@Component({
    selector: 'df-item',
    templateUrl: './form-item.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DynamicFormItemComponent implements OnChanges, OnDestroy {

    @Input() form: UntypedFormGroup;
    @Input() property: ApiModel|ApiModelRef;
    @Input() data: any;
    @Input() path: string;
    @Input() context: any;
    @Input() debug: boolean = false;

    @Input() specifications = [];
    @Output() specificationsUpdate: EventEmitter<SpecificationUpdateEvent> = new EventEmitter<SpecificationUpdateEvent>();

    model: ApiModel|ApiModelRef;
    open: boolean = false;

    private statusChangeSubscription: Subscription|null = null;
    private modelSub: Subscription|null = null;

    constructor(private models: ModelsService, private changeDetector: ChangeDetectorRef) { }


    runChangeDetection() {
        this.changeDetector.markForCheck();
        //this.changeDetector.checkNoChanges();
    }

    ngOnChanges(changes): void {
        if (changes.property != null) {
            if ((this.property as ApiModelRef).$ref != null) {
                if (this.modelSub != null) {
                    this.modelSub.unsubscribe();
                }
                this.modelSub = this.models.getModel((this.property as ApiModelRef).$ref).subscribe(model => {
                    this.model = model;
                    this.runChangeDetection();
                });
            } else {
                this.model = this.property;
            }
            this.runChangeDetection();
        }
        if (changes.path != null || changes.context != null || changes.specifications != null) {
            this.runChangeDetection();
        }
        if (changes.form != null) {
            this.runChangeDetection();
            if (this.form != null && this.model != null) {
                const control = this.form.controls[this.model['x-key']];
                if (control != null) {
                    if (this.statusChangeSubscription != null) {
                        this.statusChangeSubscription.unsubscribe();
                    }
                    this.statusChangeSubscription = control.statusChanges.subscribe(() => {
                        this.runChangeDetection();
                    });
                }
            }
        }
    }

    ngOnDestroy(): void {
        if (this.modelSub != null) {
            this.modelSub.unsubscribe();
        }
        if (this.statusChangeSubscription != null) {
            this.statusChangeSubscription.unsubscribe();
        }
    }

    type(): string {
        if (this.model == null || this.model.type == null) {
            return null;
        }
        let type = this.model.type;
        if (type === 'string') {
            if (this.model.enum != null) {
                type = 'enum';
            }
        }
        if (type === 'object' || type === 'array') {
            if (this.model['x-reference'] != null) {
                type = 'reference';
            } else if (this.model['x-taxonomy'] != null) {
                type = 'taxonomy';
            }
        }
        return type;
    }

    translatedEnum(item) {
        if (this.model['x-enumTranslation'] != null) {
            if (this.model['x-enumTranslation'][item] != null) {
                return this.model['x-enumTranslation'][item];
            }
        }
        return item;
    }

    isCollapsible() {
        if (this.type() === 'object' || this.type() === 'array') {
            return true;
        }
        return false;
    }

    isCollapsed() {
        return this.isCollapsible() && !this.open && !(this.property != null && this.property['x-key'].startsWith('measure'));
    }

    isHidden() {
        if (this.property != null) {
            if (this.property.readOnly) {
                return true;
            }
            if (this.property['x-hidden']) {
                return true;
            }
            if (this.property['x-key'] === 'id') {
                return true;
            }
        }
        return false;
    }

    toggleOpen() {
        this.open = !this.open;
        return;
    }

    get isValid() {
        return this.form == null || this.form.controls[this.model['x-key']].valid;
    }

    get error() {
        if (this.form == null || this.form.controls[this.model['x-key']].valid) {
            return '';
        }
        const errors = this.form.controls[this.model['x-key']].errors;
        if (errors) {
            if (errors.maxlength) {
                return 'Nur '  + errors.maxlength.requiredLength + ' Zeichen erlaubt.';
            }
            if (errors.pattern) {
                return 'Der Eingegebene Text hat nicht das erwartete Format.'
            }
            if (errors.required) {
                return 'Dieses Feld muss noch ausgefüllt werden.';
            }
            if (errors.null) {
                return 'Dieses Feld muss noch ausgefüllt werden.';
            }
            if (errors.nestedError) {
                return 'Überprüfen sie bitte die Eingabe.';
            }
            console.log(errors);
        }
        return 'Überprüfen sie bitte die Eingabe.';
    }

}

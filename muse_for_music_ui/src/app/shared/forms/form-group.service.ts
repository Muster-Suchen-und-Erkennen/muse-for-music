import { Injectable } from '@angular/core';
import { FormControl, FormGroup, Validators, ValidatorFn, AbstractControl } from '@angular/forms';

import { ApiModel } from '../rest/api-model';

function customNullValidator(customNull: any): ValidatorFn {
    return (control: AbstractControl): {[key: string]: any} => {
        if (control.value === customNull ||
            (customNull != null && customNull.id != null &&
             control.value != null && control.value.id === customNull.id)) {
            return {'null': {value: null}}
        }
        return null;
    };
}

@Injectable()
export class FormGroupService {
    constructor() { }

    toFormGroup(model: ApiModel): FormGroup {
        const group: {[key: string]: AbstractControl} = {};
        if (model.properties != null) {
            for (const key in model.properties) {
                if (!model.properties.hasOwnProperty(key)) {
                    continue;
                }
                const itemModel = model.properties[key];
                let value = null;
                const validators = [];
                if (itemModel.hasOwnProperty('x-required')) {
                    validators.push(Validators.required);
                }
                if (itemModel.hasOwnProperty('minLength')) {
                    validators.push(Validators.minLength((itemModel as ApiModel).minLength));
                }
                if (itemModel.hasOwnProperty('maxLength')) {
                    validators.push(Validators.maxLength((itemModel as ApiModel).maxLength));
                }
                if (itemModel.hasOwnProperty('minimum')) {
                    validators.push(Validators.min((itemModel as ApiModel).minimum));
                }
                if (itemModel.hasOwnProperty('maximum')) {
                    validators.push(Validators.max((itemModel as ApiModel).maximum));
                }
                if (itemModel.hasOwnProperty('minItems')) {
                    validators.push(Validators.minLength((itemModel as ApiModel).minItems));
                }
                if (itemModel.hasOwnProperty('maxItems')) {
                    validators.push(Validators.maxLength((itemModel as ApiModel).maxItems));
                }
                if (itemModel.hasOwnProperty('pattern')) {
                    validators.push(Validators.pattern((itemModel as ApiModel).pattern));
                }
                // calculate default nullValue and set value
                if (itemModel.hasOwnProperty('x-nullValue')) {
                    // use provided value
                    value = itemModel['x-nullValue'];
                } else {
                    if (value == null) {
                        if (itemModel.type === 'string') {
                            value = '';
                        } else if (itemModel.type === 'number' || itemModel.type === 'integer') {
                            value = -1;
                        } else if (itemModel.type === 'array') {
                            value = [];
                        } else if (itemModel.type === 'boolean') {
                            value = false;
                        } else if (itemModel.hasOwnProperty('x-reference') && itemModel['x-reference'] != null) {
                            value = {'id': -1};
                        } else if (itemModel.hasOwnProperty('x-taxonomy') && itemModel['x-taxonomy'] != null) {
                            value = {'id': -1};
                        }
                        if (key === 'id') {
                            value = -1;
                        }
                    }
                }
                // null value validator
                if (!itemModel.hasOwnProperty('x-nullable') || !itemModel['x-nullable']) {
                    if ((key !== 'id' && (itemModel.type === 'number' || itemModel.type === 'integer')) ||
                        (itemModel.type !== 'array' && itemModel.type !== 'boolean')) {
                        validators.push(customNullValidator(value));
                    }
                }

                // overwrite null value with example value
                if (itemModel.hasOwnProperty('example')) {
                    value = (itemModel as ApiModel).example;
                }

                group[key] = new FormControl(value, validators);
            }
            return new FormGroup(group);
        }
    }
}

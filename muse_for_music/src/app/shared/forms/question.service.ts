import { Injectable, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { AsyncSubject } from 'rxjs/AsyncSubject';

import { ApiService } from '../rest/api.service';

import { QuestionBase, QuestionOptions } from './question-base';
import { HiddenQuestion } from './question-hidden';
import { ReferenceQuestion } from './question-reference';
import { ObjectQuestion } from './question-nested';
import { TaxonomyQuestion } from './question-taxonomy';
import { StringQuestion } from './question-string';
import { TextQuestion } from './question-text';
import { DateQuestion } from './question-date';
import { IntegerQuestion } from './question-integer';
import { DropdownQuestion } from './question-dropdown';
import { BooleanQuestion } from './question-boolean';

import { Options } from 'selenium-webdriver';

@Injectable()
export class QuestionService implements OnInit {

    private swagger: Observable<any>;

    private observables: {
        [propName: string]: AsyncSubject<QuestionBase<any>[]>;
    } = {};

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.swagger = this.api.getSpec();
    }

    // Todo: get from a remote source of question metadata
    // Todo: make asynchronous
    getQuestions(model: string): Observable<QuestionBase<any>[]> {
        if (this.swagger == null) {
            this.swagger = this.api.getSpec();
        }

        let re = /^.*\//;
        model = model.replace(re, '');

        return this.swagger.flatMap(spec => {
            if (spec == null) {
                return Observable.of([]);
            }

            if (this.observables[model] == null) {
                this.observables[model] = new AsyncSubject<QuestionBase<any>[]>();
            }

            this.parseModel(spec, model);

            return this.observables[model].asObservable();
        })

    }

    private parseModel(spec:any, modelID: string, questionOptions?: Map<string, QuestionOptions>, orderMultiplier: number = 1) {
        let recursionStart = false;
        if (questionOptions == undefined) {
            questionOptions = new Map<string, QuestionOptions>();
            recursionStart = true;
        }

        let re = /^.*\//;
        modelID = modelID.replace(re, '');

        let model = spec.definitions[modelID];

        if (model != null) {
            if (model.allOf != null) {
                let tempModel;
                for (var parent of model.allOf) {
                    if (parent.$ref != null) {
                        this.parseModel(spec, parent.$ref, questionOptions, orderMultiplier);
                    }
                    if (parent.properties != null) {
                        tempModel = parent;
                    }
                    orderMultiplier *= 100;
                }
                model = tempModel;
            }
            if (model.properties != null) {
                for (var propID in model.properties) {
                    this.updateOptions(questionOptions, propID, model, orderMultiplier);
                }
            }
        }

        if (recursionStart) {
            let questionsArray: QuestionBase<any>[] = [];
            questionOptions.forEach(options => questionsArray.push(this.getQuestion(options)));
            this.observables[modelID].next(questionsArray.sort((a, b) => a.order - b.order));
            this.observables[modelID].complete();
        }
    }

    private updateOptions(questionOptions: Map<string, QuestionOptions>, propID: string, model: any, orderMultiplier: number = 1) {
        let options: QuestionOptions = questionOptions.get(propID);
        if (options == undefined) {
            options = {
                key: propID,
                label: propID,
                order: questionOptions.size,
            };
        }
        let prop = model.properties[propID];
        if (model.required != null) {
            for (let name of model.required) {
                if (name === propID) {
                    options.required = true;
                }
            }
        }
        options.valueType = prop.type;
        if (prop.type === 'array') {
            if (prop.items != null && prop.items.$ref != null) {
                options.valueType = prop.items.$ref;
            }
        }
        options.controlType = prop.type;
        if (prop.format != null) {
            options.controlType = prop.format;
        }
        if (prop.title != null) {
            options.label = prop.title;
        }
        if (prop.description != null) {
        }

        options.readOnly = !!prop.readOnly;
        if (prop.example != null) {
            options.value = prop.example;
        }
        if (prop.enum != null) {
            options.options = prop.enum;
        }

        if (prop.minLength != null) {
            options.min = prop.minLength;
        }
        if (prop.maxLength != null) {
            options.max = prop.maxLength;
        }

        if (prop.pattern != null) {
            options.pattern = prop.pattern;
        }

        if (prop.minimum != null) {
            options.min = prop.minimum;
        }
        if (prop.maximum != null) {
            options.max = prop.maximum;
        }

        if (prop['x-order'] != null) {
            options.order = prop['x-order'] * orderMultiplier;
        }
        if (prop['x-nullable'] != null) {
            options.nullable = prop['x-nullable'];
        }
        if (prop['x-allowSave'] != null) {
            options.allowSave = prop['x-allowSave'];
        }
        if (prop['x-reference'] != null) {
            options.controlType = 'reference';
            options.valueType = prop['x-reference'];
        }
        if (prop['x-taxonomy'] != null) {
            options.controlType = 'taxonomy';
            options.valueType = prop['x-taxonomy'];
        }
        if (prop['x-isArray'] != null) {
            options.isArray = prop['x-isArray'];
        }
        if (prop['x-isNested'] != null) {
            options.controlType = 'object';
            options.valueType = prop.$ref;
        }
        if (prop['x-nullValue'] != null) {
            options.nullValue = prop['x-nullValue'];
        }

        questionOptions.set(propID, options);
    }

    private getQuestion(options: QuestionOptions): QuestionBase<any> {
        if (options.options != null) {
            return new DropdownQuestion(options);
        }
        if (options.controlType === 'reference') {
            return new ReferenceQuestion(options);
        }
        if (options.controlType === 'object' || options.controlType === 'array') {
            const qstn = new ObjectQuestion(options);
            this.getQuestions(options.valueType).subscribe(questions => qstn.nestedQuestions = questions);
            return qstn;
        }
        if (options.controlType === 'taxonomy') {
            return new TaxonomyQuestion(options);
        }
        if (options.controlType === 'date') {
            return new DateQuestion(options);
        }
        if (options.controlType === 'boolean') {
            return new BooleanQuestion(options);
        }
        if (options.controlType === 'integer') {
            return new IntegerQuestion(options);
        }
        if (options.controlType === 'string') {
            if (options.pattern != null || options.max != null) {
                return new StringQuestion(options);
            } else {
                return new TextQuestion(options);
            }
        }
        if (options.readOnly) {
            return new HiddenQuestion(options);
        }
        return new QuestionBase(options);
    }

}

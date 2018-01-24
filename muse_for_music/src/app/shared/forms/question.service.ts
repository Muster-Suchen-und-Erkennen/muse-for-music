import { Injectable, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { AsyncSubject } from 'rxjs/AsyncSubject';

import { ApiService } from '../rest/api.service';

import { QuestionBase, QuestionOptions } from './question-base';
import { HiddenQuestion } from './question-hidden';
import { ReferenceQuestion } from './question-reference';
import { TaxonomyQuestion } from './question-taxonomy';
import { StringQuestion } from './question-string';
import { TextQuestion } from './question-text';
import { DateQuestion } from './question-date';
import { IntegerQuestion } from './question-integer';
import { DropdownQuestion } from './question-dropdown';
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
        if (this.swagger == undefined) {
            this.swagger = this.api.getSpec();
        }

        return this.swagger.flatMap(spec => {
            if (spec == undefined) {
                return Observable.of([]);
            }

            if (this.observables[model] == undefined) {
                this.observables[model] = new AsyncSubject<QuestionBase<any>[]>();
            }

            this.parseModel(spec, model);

            return this.observables[model].asObservable();
        })

    }

    private parseModel(spec:any, modelID: string, questionOptions?: {[propName: string]: QuestionOptions}) {
        let recursionStart = false;
        if (questionOptions == undefined) {
            questionOptions = {};
            recursionStart = true;
        }

        let re = /^.*\//;
        modelID = modelID.replace(re, '');

        let model = spec.definitions[modelID];

        if (model != undefined) {
            if (model.allOf != undefined) {
                let tempModel;
                for (var parent of model.allOf) {
                    if (parent.$ref != undefined) {
                        this.parseModel(spec, parent.$ref, questionOptions);
                    }
                    if (parent.properties != undefined) {
                        tempModel = parent;
                    }
                }
                model = tempModel;
            }
            if (model.properties != undefined) {
                for (var propID in model.properties) {
                    this.updateOptions(questionOptions, propID, model);
                }
            }
        }

        if (recursionStart) {
            let questionsArray: QuestionBase<any>[] = [];
            for (var question in questionOptions) {
                questionsArray.push(this.getQuestion(questionOptions[question]));
            }
            this.observables[modelID].next(questionsArray.sort((a, b) => a.order - b.order));
            this.observables[modelID].complete();
        }
    }

    private updateOptions(questionOptions: { [propName: string]: QuestionOptions; }, propID: string, model: any) {
        let options: QuestionOptions = questionOptions[propID];
        if (options == undefined) {
            options = {
                key: propID,
                label: propID,
            };
        }
        let prop = model.properties[propID];
        if (model.required != undefined) {
            for (let name of model.required) {
                if (name === propID) {
                    options.required = true;
                }
            }
        }
        options.valueType = prop.type;
        options.controlType = prop.type;
        if (prop.format != undefined) {
            options.controlType = prop.format;
        }
        if (prop.title != undefined) {
            options.label = prop.title;
        }
        if (prop.description != undefined) {
            let re = /\{.*\}/;
            let matches = prop.description.match(re);
            if (matches != null && matches.length >= 1) {
                let temp = JSON.parse(matches[0]);
                if (temp.reference != undefined) {
                    options.controlType = 'reference';
                    options.valueType = temp.reference;
                }
                if (temp.taxonomy != undefined) {
                    options.controlType = 'taxonomy';
                    options.valueType = temp.taxonomy;
                }
                if (temp.isArray != undefined) {
                    options.isArray = temp.isArray;
                }
            }
        }
        options.readOnly = !!prop.readOnly;
        if (prop.example != undefined) {
            options.value = prop.example;
        }
        if (prop.enum != undefined) {
            options.options = prop.enum;
        }

        if (prop.minLength != undefined) {
            options.min = prop.minLength;
        }
        if (prop.maxLength != undefined) {
            options.max = prop.maxLength;
        }

        questionOptions[propID] = options;
    }

    private getQuestion(options: QuestionOptions): QuestionBase<any> {
        if (options.options != undefined) {
            return new DropdownQuestion(options);
        }
        if (options.controlType === 'reference') {
            return new ReferenceQuestion(options);
        }
        if (options.controlType === 'taxonomy') {
            return new TaxonomyQuestion(options);
        }
        if (options.controlType === 'date') {
            return new DateQuestion(options);
        }
        if (options.controlType === 'integer') {
            return new IntegerQuestion(options);
        }
        if (options.controlType === 'string') {
            if (options.pattern != undefined || options.max != undefined) {
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

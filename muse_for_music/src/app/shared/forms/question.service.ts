import { Injectable, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { AsyncSubject } from 'rxjs/AsyncSubject';

import { ApiService } from '../rest/api.service';

import { QuestionBase, QuestionOptions } from './question-base';
import { StringQuestion } from './question-string';
import { DateQuestion } from './question-date';
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

            // let questions: QuestionBase<any>[] = [
            //     new StringQuestion({
            //         key: 'name',
            //         label: 'name',
            //         value: 'Unbekannt',
            //         required: true,
            //         order: 1
            //     }),
            //     new DateQuestion({
            //         key: 'birth_date',
            //         label: 'Geburtstag',
            //         value: '',
            //         required: false,
            //         order: 2
            //     })
            // ];questions.sort((a, b) => a.order - b.order);

            return this.observables[model].asObservable();
        })

    }

    private parseModel(spec:any, modelID: string, questions?: {[propName: string]: QuestionOptions}) {
        let recursionStart = false;
        if (questions == undefined) {
            questions = {};
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
                        this.parseModel(spec, parent.$ref, questions);
                    }
                    if (parent.properties != undefined) {
                        tempModel = parent;
                    }
                }
                model = tempModel;
            }
            if (model.properties != undefined) {
                for (var propID in model.properties) {
                    let options: QuestionOptions = questions[propID];
                    if (options == undefined) {
                        options = {
                            key: propID,
                            label: propID,
                        }
                    }
                    let prop = model.properties[propID];
                    if (model.required != undefined) {
                        for (var name of model.required) {
                            if (name === propID) {
                                options.required = true;
                            }
                        }
                    }
                    options.controlType = prop.type;
                    if (prop.format != undefined) {
                        options.controlType = prop.format;
                    }
                    if (prop.title != undefined) {
                        options.label = prop.title;
                    }
                    if (!!prop.readOnly) {
                        options.controlType = 'hidden';
                    }
                    if (prop.example != undefined) {
                        options.value = prop.example;
                    }
                    if (prop.enum != undefined) {
                        options.options = prop.enum;
                    }

                    questions[propID] = options;
                }
            }
        }

        if (recursionStart) {
            let questionsArray: QuestionBase<any>[] = [];
            for (var question in questions) {
                questionsArray.push(this.getQuestion(questions[question]));
            }
            this.observables[modelID].next(questionsArray.sort((a, b) => a.order - b.order));
            this.observables[modelID].complete();
        }
    }

    private getQuestion(options: QuestionOptions): QuestionBase<any> {
        console.log('####################################################');
        console.log(options);
        if (options.options != undefined) {
            return new DropdownQuestion(options);
        }
        if (options.controlType === 'date') {
            return new DateQuestion(options);
        }
        if (options.controlType === 'string') {
            return new StringQuestion(options);
        }
        return null;
    }

}

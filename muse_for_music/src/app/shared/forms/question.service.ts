import { Injectable } from '@angular/core';

import { DropdownQuestion } from './question-dropdown';
import { QuestionBase } from './question-base';
import { StringQuestion } from './question-string';
import { DateQuestion } from './question-date';

@Injectable()
export class QuestionService {

    // Todo: get from a remote source of question metadata
    // Todo: make asynchronous
    getQuestions() {

        let questions: QuestionBase<any>[] = [
            new StringQuestion({
                key: 'name',
                label: 'name',
                value: 'Unbekannt',
                required: true,
                order: 1
            }),
            new DateQuestion({
                key: 'birth_date',
                label: 'Geburtstag',
                value: '',
                required: false,
                order: 2
            })
        ];

        return questions.sort((a, b) => a.order - b.order);
    }
}
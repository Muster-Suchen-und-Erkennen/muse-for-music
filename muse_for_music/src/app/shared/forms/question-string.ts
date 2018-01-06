import { QuestionBase } from './question-base';

export class StringQuestion extends QuestionBase<string> {
    controlType = 'string';
    type: string;

    constructor(options: {} = {}) {
        super(options);
        this.type = options['type'] || '';
    }
}
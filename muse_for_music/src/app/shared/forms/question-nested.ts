import { QuestionBase, QuestionOptions } from './question-base';
import { ApiObject } from '../rest/api-base.service';

export class ObjectQuestion extends QuestionBase<ApiObject> {
    type: 'nested';
    nestedQuestions?: QuestionBase<any>[];

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'nested';
        this.nullValue = options.nullValue;
    }
}

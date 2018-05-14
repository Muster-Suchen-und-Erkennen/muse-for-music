import { QuestionBase, QuestionOptions } from './question-base';
import { ApiObject } from '../rest/api-base.service';

export class ReferenceQuestion extends QuestionBase<ApiObject|ApiObject[]> {
    controlType = 'reference';
    type: 'reference';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'reference';
        this.nullValue = options.nullValue || {'id': -1};
        if (this.isArray) {
            this.nullValue = [];
        }
    }
}

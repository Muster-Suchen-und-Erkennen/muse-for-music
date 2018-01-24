import { QuestionBase, QuestionOptions } from './question-base';
import { ApiObject } from '../rest/api-base.service';

export class TaxonomyQuestion extends QuestionBase<ApiObject> {
    controlType = 'taxonomy';
    type: 'taxonomy';

    constructor(options: QuestionOptions = {}) {
        super(options);
        this.type = options['type'] || 'taxonomy';
        this.nullValue = options.nullValue || {'id': -1};
    }
}

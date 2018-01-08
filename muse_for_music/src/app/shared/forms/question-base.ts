
export interface QuestionOptions {
    value?: any;
    key?: string,
    label?: string,
    required?: boolean,
    readOnly?: boolean,
    min?: number | string,
    max?: number | string,
    pattern?: string,
    options?: Array<any>,
    nullValue?: any,
    order?: number,
    controlType?: string;
}

export class QuestionBase<T>{
    value: T;
    key: string;
    label: string;
    required: boolean;
    order: number;
    controlType: string;

    constructor(options: QuestionOptions = {}) {
        this.value = (options.value as T);
        this.key = options.key || '';
        this.label = options.label || '';
        this.required = !!options.required;
        this.order = options.order === undefined ? 1 : options.order;
        this.controlType = options.controlType || '';
    }
}

export interface ApiModelProperties {
    [propName: string]: ApiModel | ApiModelRef | ApiModelAllOf
}

export interface ApiModelRef {
    $ref: string;
    title?: string;
    description?: string;
    [propName: string]: any;
}

export interface ApiModel {
    type: string;
    properties?: ApiModelProperties;
    required?: string[];
    title?: string;
    description?: string;
    items?: ApiModel | ApiModelRef | ApiModelAllOf
    [propName: string]: any;
}

export interface ApiModelAllOf {
    allOf: (ApiModel|ApiModelRef)[];
    title?: string;
    description?: string;
    [propName: string]: any;
}

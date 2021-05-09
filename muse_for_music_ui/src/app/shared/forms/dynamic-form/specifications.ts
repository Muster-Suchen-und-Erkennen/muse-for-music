import { ApiObject } from "app/shared/rest/api-base.service";

export interface Specification {
    path: string;
    share: ApiObject;
    occurence: ApiObject;
    instrumentation: ApiObject[];
}



import {timeout, first, reduce, mergeMap, concatMap, map} from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { InfoService } from '../info/info.service';
import { Observable, Subject, of, from, AsyncSubject } from 'rxjs';
import { ApiService } from './api.service';
import { ApiModel, ApiModelAllOf, ApiModelRef, ApiModelProperties } from './api-model';


interface PropertyMergeRef {
    key: string;
    targetProperty: ApiModel | ApiModelRef;
    sourceProperty?: ApiModel | ApiModelRef;
}

interface PropertyRef {
    key: string;
    property: ApiModel | ApiModelRef;
}


@Injectable()
export class ModelsService {

    private modelCache: Map<string, AsyncSubject<ApiModel>> = new Map<string, AsyncSubject<ApiModel>>();

    private nestedModelCache: Map<string, ApiModel> = new Map<string, ApiModel>();

    constructor(private api: ApiService) { }


    /**
     * Canonize a resource url.
     *
     * (Remove schema, host, port, api path prefix and leading/trailing slashes.)
     *
     * @param modelURL resource url
     */
    private canonizeModelUri(modelUri: string): string {
        // TODO implement
        modelUri = modelUri.replace(/^#\/definitions/, 'remote');
        if (!modelUri.includes('/')) {
            modelUri = 'remote/' + modelUri;
        }
        return modelUri;
    }


    /**
     * Resolve the modelUrl and return the corresponding model.
     *
     * @param modelUrl resource url
     */
    private resolveModel = (modelUrl: string): Observable<ApiModelAllOf | ApiModel> => {
        modelUrl = this.canonizeModelUri(modelUrl);
        if (modelUrl.startsWith('remote/')) {

            const modelID = modelUrl.substring(7);

            return this.api.getSpec().pipe(map(swaggerSpec => {
                return JSON.parse(JSON.stringify(swaggerSpec.definitions[modelID]));
            }));
        } else if (modelUrl.startsWith('nested/')) {

            const modelID = modelUrl.substring(7);

            const model = JSON.parse(JSON.stringify(this.nestedModelCache.get(modelID)));

            return of(model);
        }
        return of(null);
    }

    /**
     * Resolve all model links and return an observable of pure ApiModels
     *
     * starting with the first model of an allOf and recursively applying itself
     *
     * @param model input model
     */
    private resolveModelLinks = (model: ApiModelAllOf | ApiModelRef | ApiModel): Observable<ApiModel> => {
        if ((model as ApiModelAllOf).allOf != null) {
            const models = (model as ApiModelAllOf).allOf;
            return from(models).pipe(concatMap(this.resolveModelLinks),map(resolvedModel => {
                for (const key in model) { // inject known attributes into resolved models
                    if (key !== 'allOf' && model.hasOwnProperty(key)) {
                        resolvedModel[key] = model[key];
                    }
                }
                return resolvedModel;
            }),);
        } else if ((model as ApiModelRef).$ref != null) {
            return this.resolveModel((model as ApiModelRef).$ref).pipe(concatMap(this.resolveModelLinks),map(resolvedModel => {
                for (const key in model) { // inject known attributes into resolved models
                    if (key !== '$ref' && model.hasOwnProperty(key)) {
                        resolvedModel[key] = model[key];
                    }
                }
                return resolvedModel;
            }),);
        } else {
            return of(model as ApiModel);
        }
    }

    /**
     * Resolves all properties to actual ApiModels.
     *
     * @param model input model
     */
    private resolveProperties = (model: ApiModel): Observable<ApiModel> => {
        const props: PropertyRef[] = [];
        for (const key in model.properties) {
            if (model.properties.hasOwnProperty(key)) {
                const prop = model.properties[key];
                props.push({ key: key, property: (prop as ApiModel | ApiModelRef) });
            }
        }
        return of(...props).pipe(
            mergeMap(propRef => {
                const oldProp: any = {};
                for (const key in propRef.property) {
                    if (propRef.property.hasOwnProperty(key)) {
                        if (key === '$ref' || key === 'allOf') {
                            continue;
                        }
                        oldProp[key] = propRef.property[key];
                    }
                }
                return this
                    .resolveModelLinks(propRef.property).pipe(
                    reduce(this.mergeModels, null),
                    map(property => {
                        // merge attributes of top level last
                        this.mergeModels(property, oldProp);
                        propRef.property = property;
                        return propRef;
                    }),);
            }),
            map(propRef => {
                propRef.property['x-key'] = propRef.key;
                return propRef;
            }),
            reduce((properties: ApiModelProperties, propRef: PropertyRef) => {
                properties[propRef.key] = propRef.property;
                return properties;
            }, {}),
            map((properties) => {
                model.properties = properties;
                return model;
            }),);
    }

    /**
     * Merge two ApiModels into one model.
     *
     * @param targetModel the model to be merged into
     * @param sourceModel the model to be merged
     */
    private mergeModels = (targetModel: ApiModel | ApiModelRef, sourceModel: ApiModel | ApiModelRef): ApiModel | ApiModelRef => {
        if (targetModel == null) {
            // return next in line
            return sourceModel;
        }
        if (sourceModel == null) {
            return targetModel;
        }

        // merge models
        for (const key in sourceModel) {
            if (!sourceModel.hasOwnProperty(key)) {
                continue;
            }
            if (key === 'required') {
                // merge reqired attributes list
                if (targetModel[key] != null) {
                    const required = new Set<string>(targetModel[key]);
                    sourceModel[key].forEach(required.add.bind(required));
                    targetModel[key] = Array.from(required);
                }
            } else if (key === 'properties') {
                // skip properties in this step
            } else {
                targetModel[key] = sourceModel[key];
            }
        }

        // merge properties
        targetModel.properties = this.mergeProperties(targetModel, sourceModel);

        return targetModel;
    }


    /**
     * Merge properties of two ApiModels into one merged properties object.
     *
     * @param targetModel the model to be merged into
     * @param sourceModel the model to be merged
     */
    private mergeProperties(targetModel: ApiModel | ApiModelRef, sourceModel: ApiModel | ApiModelRef): { [prop: string]: ApiModel | ApiModelRef } {
        const propMap: Map<string, PropertyMergeRef> = new Map();

        let highestOrder = 0;

        for (const propKey in targetModel.properties) {
            if (targetModel.properties.hasOwnProperty(propKey)) {
                const prop = targetModel.properties[propKey];
                if (prop['x-order'] != null && prop['x-order'] > highestOrder) {
                    highestOrder = prop['x-order'];
                }
                propMap.set(propKey, { key: propKey, targetProperty: prop });
            }
        }

        for (const propKey in sourceModel.properties) {
            if (sourceModel.properties.hasOwnProperty(propKey)) {
                if (propMap.has(propKey)) {
                    propMap.get(propKey).sourceProperty = sourceModel.properties[propKey];
                } else {
                    const prop = sourceModel.properties[propKey];
                    if (prop['x-order'] != null) {
                        prop['x-order'] += highestOrder;
                    }
                    propMap.set(propKey, { key: propKey, targetProperty: prop});
                }
            }
        }


        const mergedProps: { [prop: string]: ApiModel | ApiModelRef } = {};

        Array.from(propMap.values()).forEach(propMergeRef => {
            mergedProps[propMergeRef.key] = this.mergeModels(propMergeRef.targetProperty, propMergeRef.sourceProperty);
        });

        return mergedProps;
    }

    /**
     * Handle object type properties.
     *
     * Replaces prop with ApiModelRef to nestedModelCache if needed
     *
     * @param propRef input PropertyRef
     */
    private handleObjectProperties = (propRef: PropertyRef): Observable<PropertyRef> => {
        if (!propRef.property.hasOwnProperty('type') || (propRef.property as ApiModel).type !== 'object') {
            return of(propRef);
        }

        let key: string;
        if (propRef.property.title != null) {
            key = `${propRef.property.title}.${propRef.key}`;
        } else {
            key = `${propRef.key}-${Date.now()}`;
        }
        this.nestedModelCache.set(key, (propRef.property as ApiModel));

        const property: ApiModelRef = {
            $ref: `nested/${key}`,
        }

        for (const key in propRef.property) {
            if (propRef.property.hasOwnProperty(key)) {
                if (key.startsWith('x-')) {
                    property[key] = propRef.property[key];
                }
                if (key === 'title') {
                    property[key] = propRef.property[key];
                }
                if (key === 'description') {
                    property[key] = propRef.property[key];
                }
            }
        }

        return of({
            key: propRef.key,
            property: property,
        });
    }


    /**
     * Handle array type properties.
     *
     * Replaces items with ApiModelRef to nestedModelCache if needed
     *
     * @param propRef input PropertyRef
     */
    private handleArrayProperties = (propRef: PropertyRef): Observable<PropertyRef> => {
        if (!propRef.property.hasOwnProperty('type') || (propRef.property as ApiModel).type !== 'array') {
            return of(propRef);
        }

        const items = (propRef.property as ApiModel).items;
        if (items.$ref != null) {
            return of(propRef);
        }
        let key: string;
        if (propRef.property != null && propRef.property.title != null) {
            key = `${propRef.property.title}.${propRef.key}`;
        } else {
            key = `${propRef.key}-${Date.now()}`;
        }
        this.nestedModelCache.set(key, (items as ApiModel));
        const propCopy = JSON.parse(JSON.stringify(propRef.property));
        propCopy.items = {
            $ref: `nested/${key}`,
        };

        return of({
            key: propRef.key,
            property: propCopy,
        });
    }

    /**
     * Check all properties of model for complex properties like arrays or objects.
     *
     * Replaces all nested models with ApiModelRefs to nestedModelCache
     *
     * @param model input model
     */
    private handleComplexProperties = (model: ApiModel): Observable<ApiModel> => {
        const props: PropertyRef[] = [];
        for (const key in model.properties) {
            if (model.properties.hasOwnProperty(key)) {
                const prop = model.properties[key];
                props.push({ key: key, property: (prop as ApiModel | ApiModelRef) });
            }
        }
        return of(...props).pipe(
            mergeMap(this.handleObjectProperties),
            mergeMap(this.handleArrayProperties),
            reduce((properties, propRef: PropertyRef) => {
                if (propRef.property.title == null) {
                    propRef.property.title = propRef.key;
                }
                properties[propRef.key] = propRef.property;
                return properties;
            }, {}),
            map((properties) => {
                model.properties = properties;
                return model;
            }),);
    }


    /**
     * Fetch the cache source for the given model url.
     *
     * @param cacheUrl resource url
     */
    private getCacheSource = (cacheURL: string): AsyncSubject<ApiModel> => {
        cacheURL = this.canonizeModelUri(cacheURL);
        let stream = this.modelCache.get(cacheURL);
        if (stream == null) {
            stream = new AsyncSubject<Readonly<ApiModel>>();
            this.modelCache.set(cacheURL, stream);
        }
        return stream;
    }

    /**
     * Get a model for the modelUrl.
     *
     * Observable only sends a value if the model was found.
     * Times out after 2s
     *
     * @param modelUrl modelUrl
     */
    getModel = (modelUrl): Observable<ApiModel> => {
        const stream = this.getCacheSource(modelUrl);
        if (!stream.closed) {
            this.resolveModel(modelUrl).pipe(
                concatMap(this.resolveModelLinks),
                mergeMap(this.resolveProperties),
                reduce(this.mergeModels, null),
                mergeMap(this.handleComplexProperties),
                map(model => {
                    // inject required information into property
                    if (model.required != null && model.properties != null) {
                        model.required.forEach(key => {
                            const prop = model.properties[key];
                            if (prop != null) {
                                prop['x-required'] = true;
                            }
                        });
                    }
                    return model;
                }),
                first(),)
                .subscribe((model) => {
                    if (model != null) {
                        stream.next(model);
                        stream.complete();
                    }
                });
        }
        return stream.asObservable().pipe(timeout(2000),first(),);
    }

    /**
     * Return a stream filter for api models. (use with map in observable pipe)
     *
     * @param properties the property keys to filter for (array/set or other iterable)
     *                   Use Empty iterable or null to deactivate filter
     * @param isBlacklist if true the filter ill be appliead as blacklist. (default=whitelest/false)
     */
    filterModel(properties: Iterable<string>, isBlacklist: boolean = false): (ApiModel) => ApiModel {
        const filterset: Set<string> = (properties !== null) ? new Set<string>(properties) : new Set<string>();
        return (model) => {
            if (filterset.size === 0) { return model; }
            const newModel: ApiModel = { type: model.type };
            for (const key in model) {
                if (key === 'type') {
                    continue;
                } else if (key === 'properties') {
                    const props = model[key];
                    const newProps: any = {};
                    for (const propKey in props) {
                        if ((isBlacklist && !filterset.has(propKey)) ||
                            (!isBlacklist && filterset.has(propKey))) {
                            newProps[propKey] = JSON.parse(JSON.stringify(props[propKey]));
                        }
                    }
                    newModel[key] = newProps;
                    continue;
                } else if (key === 'required') {
                    if (isBlacklist) {
                        newModel[key] = model[key].filter((propKey) => !filterset.has(propKey));
                    } else {
                        newModel[key] = model[key].filter((propKey) => filterset.has(propKey));
                    }
                    continue;
                }
                newModel[key] = model[key];
            }
            return newModel;
        };
    }
}

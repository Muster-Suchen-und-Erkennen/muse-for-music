import { Injectable, OnInit } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { InfoService } from '../info/info.service';
import { AsyncSubject } from 'rxjs/AsyncSubject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

export interface RootLinks extends ApiLinksObject {
    doc: LinkObject;
    spec: LinkObject;
    taxonomy: LinkObject;
    person: LinkObject;
    opus: LinkObject;
    part: LinkObject;
    subpart: LinkObject;
};
export interface RootModel extends ApiObject {
    _links: RootLinks;
    [propName: string]: any;
};

@Injectable()
export class ApiService implements OnInit {

    private warningSet = new Set([404, 409, ]);

    private errorSet = new Set([500, 501, ]);

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();

    private currentSpec = this.specSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<ApiObject | ApiObject[]>} = {};

    constructor(private rest: BaseApiService, private info: InfoService) {
        Observable.timer(1).take(1).subscribe((() => {
            this.ngOnInit()
        }).bind(this));
    }

    ngOnInit(): void {
        this.getRoot();
    }

    private errorHandler(error, resource: string, method: string) {
        let title;
        let message = 'Unknown Error.';
        switch (method) {
            case 'POST':
                title = 'Error while creating new resource under "' + resource + '".';
                break;
            case 'PUT':
                title = 'Error while updating existing resource "' + resource + '".';
                break;

            default:
                title = 'Error while retrieving resource "' + resource + '".'
                break;
        }
        if (error.message != null) {
            message = error.message;
        }

        if (this.errorSet.has(error.status)) {
            this.info.emitError(message, title);
        } else if (this.warningSet.has(error.status)) {
            this.info.emitWarning(message, title, 7000);
        } else {
            this.info.emitInfo(message, title, 5000);
        }
    }

    getRoot(): Observable<RootModel> {
        if (!this.rootSource.isStopped) {
            let url = '/api'
            if ((window as any).apiBasePath != undefined) {
                url = (window as any).apiBasePath;
            }
            this.rest.get(url).subscribe(data => {
                this.rootSource.next((data as RootModel));
                this.rootSource.complete();
            }, error => this.errorHandler(error, 'root', 'GET'));
        }
        return this.currentRoot;
    }

    getSpec(): Observable<any> {
        this.getRoot().subscribe(root => {
            if (!this.specSource.isStopped) {
                const re = /\/$/;
                const url = root._links.spec.href.replace(re, '');
                this.rest.get(url).subscribe(data => {
                    this.specSource.next((data as any));
                    this.specSource.complete();
                });
            }
        }, error => this.errorHandler(error, 'spec', 'GET'));
        return this.currentSpec;
    }

    private getStreamSource(streamID: string, create: boolean = true) {
        if (this.streams[streamID] == null && create) {
            this.streams[streamID] = new BehaviorSubject<ApiObject | ApiObject[]>(undefined);
        }
        return this.streams[streamID]
    }

    private updateResource(streamID: string, data: ApiObject) {
        const stream = this.getStreamSource(streamID + '/' +  data.id);
        stream.next(data);
        const list_stream = this.getStreamSource(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue() as ApiObject[]);
            if (list != null) {
                const index = list.findIndex(value => value.id === data.id);
                if (index < 0) {
                    list.push(data);
                } else {
                    list[index] = data;
                }
                list_stream.next(list);
            }
        }
    }

    getTaxonomies(): Observable<ApiObject> {
        const resource = 'taxonomies';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.taxonomy).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getTaxonomy(taxonomy: string): Observable<ApiObject> {
        const baseResource = 'taxonomies';
        const resource = baseResource + '/' + taxonomy.toUpperCase();
        const stream = this.getStreamSource(resource);
        this.getTaxonomies().subscribe(taxonomies => {
            if (taxonomies === undefined) {
                return;
            }
            for (const tax of taxonomies.taxonomies) {
                if (tax.name.toUpperCase() === taxonomy.toUpperCase()) {
                    this.rest.get(tax._links.self).subscribe(data => {
                        stream.next(data);
                    });
                }
            }
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getPeople(): Observable<Array<ApiObject>> {
        const resource = 'persons';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    getPerson(id: number): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person.href + id + '/').subscribe(data => {
                this.updateResource(resource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postPerson(newData): Observable<ApiObject> {
        const resource = 'persons';
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.person, newData).flatMap(data => {
                const stream = this.getStreamSource(resource + '/' + data.id);
                this.updateResource(resource, data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    putPerson(id: number, newData): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.person.href + id + '/', newData).subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getOpuses(): Observable<ApiObject[]> {
        const resource = 'opuses';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    getOpus(id: number): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus.href + id + '/').subscribe(data => {
                this.updateResource(resource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postOpus(newData): Observable<ApiObject> {
        const resource = 'opuses';
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.opus, newData).flatMap(data => {
                const stream = this.getStreamSource(resource + '/' + data.id);
                this.updateResource(resource, data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    putOpus(id: number, newData): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.opus.href + id + '/', newData).subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getParts(opus?: ApiObject): Observable<ApiObject[]> {
        let resource = 'parts';
        let stream = this.getStreamSource(resource);
        if (opus === undefined) {
            this.getRoot().subscribe(root => {
                this.rest.get(root._links.part).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        } else {
            resource = 'opuses/' + opus.id + '/parts';
            stream = this.getStreamSource(resource)
            this.rest.get(opus._links.part).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    postPart(opus: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'parts';
        return this.rest.post(opus._links.part, data).flatMap(data => {
            const stream = this.getStreamSource(resource + '/' + data.id);
            this.updateResource(resource, data as ApiObject);
            return (stream.asObservable() as Observable<ApiObject>);
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    getSubParts(): Observable<ApiObject[]> {
        const stream = this.getStreamSource('subparts');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.subpart).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }
}

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
                case 'DELETE':
                    title = 'Error while deleting existing resource "' + resource + '".';
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
            if ((window as any).apiBasePath != null) {
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
        return this.streams[streamID];
    }

    private updateResource(streamID: string, data: ApiObject) {
        const stream = this.getStreamSource(streamID + '/' +  data.id);
        stream.next(data);
        this.updateListResource(streamID, data);
    }

    private updateListResource(streamID: string, data: ApiObject) {
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

    private removeResource(streamID: string, id: number) {
        const stream = this.getStreamSource(streamID + '/' + id);
        stream.next(null);
        this.removeListResource(streamID, id);
    }

    private removeListResource(streamID: string, id: number) {
        const list_stream = this.getStreamSource(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue() as ApiObject[]);
            if (list != null) {
                const index = list.findIndex(value => value.id === id);
                if (index >= 0) {
                    list.splice(index, 1);
                    list_stream.next(list);
                }
            }
        }
    }


    /// Taxonomies /////////////////////////////////////////////////////////////
    getTaxonomies(): Observable<ApiObject> {
        const resource = 'taxonomies';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.taxonomy).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
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
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }


    /// People /////////////////////////////////////////////////////////////////
    getPeople(): Observable<Array<ApiObject>> {
        const resource = 'persons';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data !== undefined);
    }

    getPerson(id: number): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person.href + id + '/').subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    postPerson(newData): Observable<ApiObject> {
        const resource = 'persons';
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.person, newData).flatMap(data => {
                const stream = this.getStreamSource(resource + '/' + data.id);
                this.updateResource(resource, data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
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
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    deletePerson(person: ApiObject): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + person.id;
        const stream = this.getStreamSource(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.person.href + person.id + '/').subscribe(() => {
                this.removeResource(baseResource, person.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }


    /// Opuses /////////////////////////////////////////////////////////////////
    getOpuses(): Observable<ApiObject[]> {
        const resource = 'opuses';
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data !== undefined);
    }

    getOpus(id: number): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus.href + id + '/').subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    postOpus(newData): Observable<ApiObject> {
        const resource = 'opuses';
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.opus, newData).flatMap(data => {
                const stream = this.getStreamSource(resource + '/' + data.id);
                this.updateResource(resource, data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
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
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    deleteOpus(id: number): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.opus.href + id + '/').subscribe(() => {
                this.removeResource(baseResource, id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }


    /// Parts //////////////////////////////////////////////////////////////////
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
        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data !== undefined);
    }

    getPart(id: number): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.part.href + id + '/').subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
                this.updateListResource('opuses' + '/' + (data as ApiObject).opus_id + '/parts', data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    postPart(opus: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'parts';
        return this.rest.post(opus._links.part, data).flatMap(data => {
            const stream = this.getStreamSource(resource + '/' + data.id);
            this.updateResource(resource, data as ApiObject);
            this.updateListResource('opuses' + '/' + data.opus_id + '/parts', data as ApiObject);
            return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    putPart(id: number, newData): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.part.href + id + '/', newData).subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
                this.updateListResource('opuses' + '/' + data.opus_id + '/parts', data as ApiObject);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    deletePart(part: ApiObject): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + part.id;
        const stream = this.getStreamSource(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.part.href + part.id + '/').subscribe(() => {
                this.removeResource(baseResource, part.id);
                this.removeListResource('opuses' + '/' + part.opus_id + '/parts', part.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }


    /// SubpParts //////////////////////////////////////////////////////////////
    getSubParts(part?: ApiObject): Observable<ApiObject[]> {
        let resource = 'subparts';
        let stream = this.getStreamSource(resource);
        if (part === undefined) {
            this.getRoot().subscribe(root => {
                this.rest.get(root._links.subpart).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        } else {
            resource = 'parts/' + part.id + '/subparts';
            stream = this.getStreamSource(resource)
            this.rest.get(part._links.subpart).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }
        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data !== undefined);
    }

    getSubPart(id: number): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.subpart.href + id + '/').subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
                this.updateListResource('parts' + '/' + (data as ApiObject).part_id + '/subparts', data as ApiObject);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    postSubPart(part: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'subparts';
        return this.rest.post(part._links.subpart, data).flatMap(data => {
            const stream = this.getStreamSource(resource + '/' + data.id);
            this.updateResource(resource, data as ApiObject);
            this.updateListResource('parts' + '/' + data.part_id + '/subparts', data as ApiObject);
            return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    putSubPart(id: number, newData): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.subpart.href + id + '/', newData).subscribe(data => {
                this.updateResource(baseResource, data as ApiObject);
                this.updateListResource('parts' + '/' + data.part_id + '/subparts', data as ApiObject);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    deleteSubPart(subpart: ApiObject): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + subpart.id;
        const stream = this.getStreamSource(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.subpart.href + subpart.id + '/').subscribe(() => {
                this.removeResource(baseResource, subpart.id);
                this.removeListResource('parts' + '/' + subpart.part_id + '/subparts', subpart.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }


    /// Voices /////////////////////////////////////////////////////////////////
    getVoices(subpart: ApiObject): Observable<ApiObject[]> {
        const resource = 'subparts/' + subpart.id + '/voices';
        const stream = this.getStreamSource(resource);
        this.rest.get(subpart._links.voice).subscribe(data => {
            stream.next(data);
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject[]>).filter(data => data !== undefined);
    }

    getVoice(subpart: ApiObject, id: number): Observable<ApiObject> {
        const baseResource = 'subparts/' + subpart.id + '/voices';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.rest.get(subpart._links.voice.href + id + '/').subscribe(data => {
            this.updateResource(baseResource, data as ApiObject);
            this.updateListResource('subparts' + '/' + subpart.id + '/voices', data as ApiObject);
        }, error => this.errorHandler(error, resource, 'GET'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    postVoice(subpart: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'subparts/' + subpart.id + '/voices';
        return this.rest.post(subpart._links.voice, data).flatMap(data => {
            const stream = this.getStreamSource(resource + '/' + data.id);
            this.updateResource(resource, data as ApiObject);
            this.updateListResource('subparts' + '/' + subpart.id + '/voices', data as ApiObject);
            return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
        }).catch(error => {
            this.errorHandler(error, resource, 'POST');
            return Observable.throw(error);
        });
    }

    putVoice(subpart: ApiObject, id: number, newData): Observable<ApiObject> {
        const baseResource = 'subparts/' + subpart.id + '/voices';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource(resource);
        this.rest.put(subpart._links.voice.href + id + '/', newData).subscribe(data => {
            this.updateResource(baseResource, data as ApiObject);
            this.updateListResource('parts' + '/' + data.part_id + '/subparts', data as ApiObject);
        }, error => this.errorHandler(error, resource, 'PUT'));
        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }

    deleteVoice(subpart: ApiObject, voice: ApiObject): Observable<ApiObject> {
        const baseResource = 'subparts' + subpart.id + '/voices';
        const resource = baseResource + '/' + voice.id;
        const stream = this.getStreamSource(resource);

        this.rest.delete(subpart._links.voice.href + voice.id + '/').subscribe(() => {
            this.removeResource(baseResource, voice.id);
            this.removeListResource('subparts' + '/' + subpart.id + '/voices', voice.id);
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return (stream.asObservable() as Observable<ApiObject>).filter(data => data !== undefined);
    }
}

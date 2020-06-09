
import {throwError as observableThrowError, timer as observableTimer, Observable, AsyncSubject , BehaviorSubject } from 'rxjs';

import {catchError, mergeMap, filter, take } from 'rxjs/operators';
import { Injectable, OnInit } from '@angular/core';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { InfoService } from '../info/info.service';
import { UserApiService } from './user-api.service';

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

    private warningSet = new Set([401, 403, 404, 409, ]);

    private errorSet = new Set([500, 501, ]);

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();

    private currentSpec = this.specSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<any>} = {}; // FIXME change any to unknown

    constructor(private rest: BaseApiService, private userApi: UserApiService, private info: InfoService) {
        observableTimer(1).pipe(take(1)).subscribe((() => {
            this.ngOnInit()
        }).bind(this));
    }

    ngOnInit(): void {
        this.getRoot();
    }

    private errorHandler(error, resource: string, method: string) {
        let title;
        let message = 'Unbekannter Error.';
        switch (method) {
            case 'POST':
                title = 'Error beim Erstellen einer neuen Ressource unter "' + resource + '".';
                break;
            case 'PUT':
                title = 'Error beim ändern der existierenden Ressource "' + resource + '".';
                break;
                case 'DELETE':
                    title = 'Error beim löschen der Ressource "' + resource + '".';
                    break;

            default:
                title = 'Error beim Abrufen der Ressource "' + resource + '".'
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
            this.rest.get<RootModel>(url).subscribe(data => {
                this.rootSource.next(data);
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
                this.rest.get<any>(url).subscribe(data => {
                    this.specSource.next(data);
                    this.specSource.complete();
                });
            }
        }, error => this.errorHandler(error, 'spec', 'GET'));
        return this.currentSpec;
    }

    private getStreamSource<T>(streamID: string, create: boolean = true): BehaviorSubject<T> {
        if (this.streams[streamID] == null && create) {
            this.streams[streamID] = new BehaviorSubject<T>(undefined);
        }
        return this.streams[streamID] as BehaviorSubject<T>;
    }

    private updateResource(streamID: string, data: ApiObject) {
        const stream = this.getStreamSource<ApiObject>(streamID + '/' +  data.id);
        stream.next(data);
        this.updateListResource(streamID, data);
    }

    private updateListResource(streamID: string, data: ApiObject) {
        const list_stream = this.getStreamSource<ApiObject[]>(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue());
            if (list != null) {
                const newlist = [];
                let updated = false;
                list.forEach((value) => {
                    if (value.id === data.id) {
                        updated = true;
                        newlist.push(data);
                    } else {
                        newlist.push(value);
                    }
                });
                if (!updated) {
                    newlist.push(data);
                }
                list_stream.next(newlist);
            }
        }
    }

    private removeResource(streamID: string, id: number) {
        const stream = this.getStreamSource<ApiObject>(streamID + '/' + id);
        stream.next(null);
        this.removeListResource(streamID, id);
    }

    private removeListResource(streamID: string, id: number) {
        const list_stream = this.getStreamSource<ApiObject[]>(streamID, false);
        if (list_stream != null) {
            const list: ApiObject[] = (list_stream.getValue());
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
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject>(root._links.taxonomy, this.userApi.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getTaxonomy(taxonomy: string): Observable<ApiObject> {
        const baseResource = 'taxonomies';
        const resource = baseResource + '/' + taxonomy.toUpperCase();
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getTaxonomies().subscribe(taxonomies => {
            if (taxonomies === undefined) {
                return;
            }
            for (const tax of taxonomies.taxonomies) {
                if (tax.name.toUpperCase() === taxonomy.toUpperCase()) {
                    this.rest.get<ApiObject>(tax._links.self, this.userApi.token).subscribe(data => {
                        stream.next(data);
                    });
                }
            }
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postTaxonomyItem(taxonomy: ApiObject, newItem: any, parent?: ApiObject): Observable<ApiObject> {
        const baseResource = 'taxonomies';
        let resource = baseResource + '/' + taxonomy.name;
        let url = taxonomy._links.self;
        if (parent != null) {
            resource = baseResource + '/' + taxonomy.name + '/' + parent.id;
            url = parent._links.self;
        }
        return this.rest.post<ApiObject>(url, newItem, this.userApi.token).pipe(
            mergeMap(() => this.getTaxonomy(taxonomy.name)),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            })
        );
    }

    putTaxonomyItem(taxonomy: ApiObject, item: ApiObject, newValues: any): Observable<ApiObject> {
        const baseResource = 'taxonomies';
        const resource = baseResource + '/' + taxonomy.name + '/' + item.id;

        return this.rest.put<ApiObject>(item._links.self, newValues, this.userApi.token).pipe(
            mergeMap(() => this.getTaxonomy(taxonomy.name)),
            catchError(error => {
                this.errorHandler(error, resource, 'PUT');
                return observableThrowError(error);
            }),
        );
    }

    deleteTaxonomyItem(taxonomy: ApiObject, item: ApiObject): Observable<ApiObject> {
        const baseResource = 'taxonomies';
        const resource = baseResource + '/' + taxonomy.name + '/' + item.id;

        return this.rest.delete(item._links.self, this.userApi.token).pipe(
            mergeMap(() => this.getTaxonomy(taxonomy.name)),
            catchError(error => {
                this.errorHandler(error, resource, 'DELETE');
                return observableThrowError(error);
            }),
        );
    }


    /// People /////////////////////////////////////////////////////////////////
    getPeople(): Observable<ApiObject[]> {
        const resource = 'persons';
        const stream = this.getStreamSource<ApiObject[]>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject[]>(root._links.person, this.userApi.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getPerson(id: number): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject>(root._links.person.href + id + '/', this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postPerson(newData): Observable<ApiObject> {
        const resource = 'persons';
        return this.getRoot().pipe(
            mergeMap(root => {
                return this.rest.post<ApiObject>(root._links.person, newData, this.userApi.token).pipe(
                    mergeMap(data => {
                        const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                        this.updateResource(resource, data);
                        return stream.asObservable().pipe(filter(data => data !== undefined));
                    }));
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
    }

    putPerson(id: number, newData): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.put<ApiObject>(root._links.person.href + id + '/', newData, this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    deletePerson(person: ApiObject): Observable<ApiObject> {
        const baseResource = 'persons';
        const resource = baseResource + '/' + person.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.person.href + person.id + '/', this.userApi.token).subscribe(() => {
                this.removeResource(baseResource, person.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return stream.asObservable().pipe(filter(data => data !== undefined));
    }


    /// Opuses /////////////////////////////////////////////////////////////////
    getOpuses(): Observable<ApiObject[]> {
        const resource = 'opuses';
        const stream = this.getStreamSource<ApiObject[]>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject[]>(root._links.opus, this.userApi.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getOpus(id: number): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject>(root._links.opus.href + id + '/', this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postOpus(newData): Observable<ApiObject> {
        const resource = 'opuses';
        return this.getRoot().pipe(
            mergeMap(root => {
                return this.rest.post<ApiObject>(root._links.opus, newData, this.userApi.token).pipe(
                    mergeMap(data => {
                        const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                        this.updateResource(resource, data);
                        return stream.asObservable().pipe(filter(data => data !== undefined));
                    })
                );
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
    }

    putOpus(id: number, newData): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.put<ApiObject>(root._links.opus.href + id + '/', newData, this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    deleteOpus(id: number): Observable<ApiObject> {
        const baseResource = 'opuses';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.opus.href + id + '/', this.userApi.token).subscribe(() => {
                this.removeResource(baseResource, id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return stream.asObservable().pipe(filter(data => data !== undefined));
    }


    /// Parts //////////////////////////////////////////////////////////////////
    getParts(opus?: ApiObject): Observable<ApiObject[]> {
        let resource = 'parts';
        let stream = this.getStreamSource<ApiObject[]>(resource);
        if (opus === undefined) {
            this.getRoot().subscribe(root => {
                this.rest.get<ApiObject[]>(root._links.part, this.userApi.token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        } else {
            resource = 'opuses/' + opus.id + '/parts';
            stream = this.getStreamSource<ApiObject[]>(resource)
            this.rest.get<ApiObject[]>(opus._links.part, this.userApi.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getPart(id: number): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject>(root._links.part.href + id + '/', this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
                this.updateListResource('opuses' + '/' + data.opus_id + '/parts', data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postPart(opus: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'parts';
        return this.rest.post<ApiObject>(opus._links.part, data, this.userApi.token).pipe(
            mergeMap(data => {
                const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                this.updateResource(resource, data);
                this.updateListResource('opuses' + '/' + data.opus_id + '/parts', data);
                return stream.asObservable().pipe(filter(data => data !== undefined));
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
    }

    putPart(id: number, newData): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.put<ApiObject>(root._links.part.href + id + '/', newData, this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
                this.updateListResource('opuses' + '/' + data.opus_id + '/parts', data);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    deletePart(part: ApiObject): Observable<ApiObject> {
        const baseResource = 'parts';
        const resource = baseResource + '/' + part.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.part.href + part.id + '/', this.userApi.token).subscribe(() => {
                this.removeResource(baseResource, part.id);
                this.removeListResource('opuses' + '/' + part.opus_id + '/parts', part.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return stream.asObservable().pipe(filter(data => data !== undefined));
    }


    /// SubpParts //////////////////////////////////////////////////////////////
    getSubParts(part?: ApiObject): Observable<ApiObject[]> {
        let resource = 'subparts';
        let stream = this.getStreamSource<ApiObject[]>(resource);
        if (part === undefined) {
            this.getRoot().subscribe(root => {
                this.rest.get<ApiObject[]>(root._links.subpart, this.userApi.token).subscribe(data => {
                    stream.next(data);
                }, error => this.errorHandler(error, resource, 'GET'));
            }, error => this.errorHandler(error, resource, 'GET'));
        } else {
            resource = 'parts/' + part.id + '/subparts';
            stream = this.getStreamSource<ApiObject[]>(resource)
            this.rest.get<ApiObject[]>(part._links.subpart, this.userApi.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getSubPart(id: number): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.get<ApiObject>(root._links.subpart.href + id + '/', this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
                this.updateListResource('parts' + '/' + (data).part_id + '/subparts', data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postSubPart(part: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'subparts';
        return this.rest.post<ApiObject>(part._links.subpart, data, this.userApi.token).pipe(
            mergeMap(data => {
                const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                this.updateResource(resource, data);
                this.updateListResource('parts' + '/' + data.part_id + '/subparts', data);
                return stream.asObservable().pipe(filter(data => data !== undefined));
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
    }

    putSubPart(id: number, newData): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.getRoot().subscribe(root => {
            this.rest.put<ApiObject>(root._links.subpart.href + id + '/', newData, this.userApi.token).subscribe(data => {
                this.updateResource(baseResource, data);
                this.updateListResource('parts' + '/' + data.part_id + '/subparts', data);
            }, error => this.errorHandler(error, resource, 'PUT'));
        });
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    deleteSubPart(subpart: ApiObject): Observable<ApiObject> {
        const baseResource = 'subparts';
        const resource = baseResource + '/' + subpart.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.getRoot().subscribe((root) => {
            this.rest.delete(root._links.subpart.href + subpart.id + '/', this.userApi.token).subscribe(() => {
                this.removeResource(baseResource, subpart.id);
                this.removeListResource('parts' + '/' + subpart.part_id + '/subparts', subpart.id);
            }, error => this.errorHandler(error, resource, 'DELETE'));
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return stream.asObservable().pipe(filter(data => data !== undefined));
    }


    /// Voices /////////////////////////////////////////////////////////////////
    getVoices(subpart: ApiObject): Observable<ApiObject[]> {
        const resource = 'subparts/' + subpart.id + '/voices';
        const stream = this.getStreamSource<ApiObject[]>(resource);
        this.rest.get<ApiObject[]>(subpart._links.voice, this.userApi.token).subscribe(data => {
            stream.next(data);
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    getVoice(subpart: ApiObject, id: number): Observable<ApiObject> {
        const baseResource = 'subparts/' + subpart.id + '/voices';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.rest.get<ApiObject>(subpart._links.voice.href + id + '/', this.userApi.token).subscribe(data => {
            this.updateResource(baseResource, data);
            this.updateListResource('subparts' + '/' + subpart.id + '/voices', data);
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    postVoice(subpart: ApiObject, data: any): Observable<ApiObject> {
        const resource = 'subparts/' + subpart.id + '/voices';
        return this.rest.post<ApiObject>(subpart._links.voice, data, this.userApi.token).pipe(
            mergeMap(data => {
                const stream = this.getStreamSource<ApiObject>(resource + '/' + data.id);
                this.updateResource(resource, data);
                this.updateListResource('subparts' + '/' + subpart.id + '/voices', data);
                return stream.asObservable().pipe(filter(data => data !== undefined));
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
    }

    putVoice(subpart: ApiObject, id: number, newData): Observable<ApiObject> {
        const baseResource = 'subparts/' + subpart.id + '/voices';
        const resource = baseResource + '/' + id;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.rest.put<ApiObject>(subpart._links.voice.href + id + '/', newData, this.userApi.token).subscribe(data => {
            this.updateResource(baseResource, data);
            this.updateListResource('parts' + '/' + data.part_id + '/subparts', data);
        }, error => this.errorHandler(error, resource, 'PUT'));
        return stream.asObservable().pipe(filter(data => data !== undefined));
    }

    deleteVoice(subpart: ApiObject, voice: ApiObject): Observable<ApiObject> {
        const baseResource = 'subparts' + subpart.id + '/voices';
        const resource = baseResource + '/' + voice.id;
        const stream = this.getStreamSource<ApiObject>(resource);

        this.rest.delete(subpart._links.voice.href + voice.id + '/', this.userApi.token).subscribe(() => {
            this.removeResource(baseResource, voice.id);
            this.removeListResource('subparts' + '/' + subpart.id + '/voices', voice.id);
        }, error => this.errorHandler(error, resource, 'DELETE'));

        return stream.asObservable().pipe(filter(data => data !== undefined));
    }


    /// History ////////////////////////////////////////////////////////////////
    getHistory(user?: string): Observable<ApiObject[]> {
        let resource = 'history';
        if (user != null) {
            resource = resource + '/' + user;
        }
        const stream = new AsyncSubject<ApiObject[]>();
        this.getRoot().subscribe(root => {
            let url = root._links.history.href;
            if (user != null) {
                url = url + user + '/';
            }
            this.rest.get<ApiObject[]>(url, this.userApi.token).subscribe(data => {
                stream.next(data);
                stream.complete();
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable();
    }
}

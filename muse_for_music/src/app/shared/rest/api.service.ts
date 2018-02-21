import { Injectable, OnInit } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
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

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    private specSource = new AsyncSubject<any>();

    private currentSpec = this.specSource.asObservable();

    private streams: {[propName: string]: BehaviorSubject<ApiObject | ApiObject[]>} = {};

    constructor(private rest: BaseApiService) { }

    ngOnInit(): void {
        this.getRoot();
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
            });
        }
        return this.currentRoot;
    }

    getSpec(): Observable<any> {
        this.getRoot().subscribe(root => {
            if (!this.specSource.isStopped) {
                var re = /\/$/;
                let url = root._links.spec.href.replace(re, '');
                this.rest.get(url).subscribe(data => {
                    this.specSource.next((data as any));
                    this.specSource.complete();
                });
            }
        });
        return this.currentSpec;
    }

    private getStreamSource(streamID: string) {
        if (this.streams[streamID] == undefined) {
            this.streams[streamID] = new BehaviorSubject<ApiObject | ApiObject[]>(undefined);
        }
        return this.streams[streamID]
    }

    getTaxonomies(): Observable<ApiObject> {
        let stream = this.getStreamSource('taxonomies');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.taxonomy).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getTaxonomy(taxonomy: string): Observable<ApiObject> {
        let stream = this.getStreamSource('taxonomies/' + taxonomy.toUpperCase());
        this.getTaxonomies().subscribe(taxonomies => {
            if (taxonomies == undefined) {
                return;
            }
            for (let tax of taxonomies.taxonomies) {
                if (tax.name.toUpperCase() === taxonomy.toUpperCase()) {
                    this.rest.get(tax._links.self).subscribe(data => {
                        stream.next(data);
                    });
                }
            }
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getPeople(): Observable<Array<ApiObject>> {
        let stream = this.getStreamSource('persons');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    private personUpdate(data: ApiObject) {
        let stream = this.getStreamSource('persons/' + data.id);
        stream.next(data);
        // TODO update list
        this.getPeople();
    }

    getPerson(id: number): Observable<ApiObject> {
        let stream = this.getStreamSource('persons/' + id);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.person.href + id + '/').subscribe(data => {
                this.personUpdate(data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postPerson(newData): Observable<ApiObject> {
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.person, newData).flatMap(data => {
                let stream = this.getStreamSource('persons/' + data.id);
                this.personUpdate(data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        });
    }

    putPerson(id: number, newData): Observable<ApiObject> {
        let stream = this.getStreamSource('persons/' + id);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.person.href + id + '/', newData).subscribe(data => {
                this.personUpdate(data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getOpuses(): Observable<ApiObject[]> {
        let stream = this.getStreamSource('opuses');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    private opusUpdate(data: ApiObject) {
        let stream = this.getStreamSource('opuses/' + data.id);
        stream.next(data);
        // TODO update list
        this.getOpuses();
    }

    getOpus(id: number): Observable<ApiObject> {
        let stream = this.getStreamSource('opuses/' + id);
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.opus.href + id + '/').subscribe(data => {
                this.opusUpdate(data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    postOpus(newData): Observable<ApiObject> {
        return this.getRoot().flatMap(root => {
            return this.rest.post(root._links.opus, newData).flatMap(data => {
                let stream = this.getStreamSource('opuses/' + data.id);
                this.opusUpdate(data as ApiObject);
                return (stream.asObservable() as Observable<ApiObject>);
            });
        });
    }

    putOpus(id: number, newData): Observable<ApiObject> {
        let stream = this.getStreamSource('opuses/' + id);
        this.getRoot().subscribe(root => {
            this.rest.put(root._links.opus.href + id + '/', newData).subscribe(data => {
                this.opusUpdate(data as ApiObject);
            });
        });
        return (stream.asObservable() as Observable<ApiObject>);
    }

    getParts(opus?: ApiObject): Observable<ApiObject[]> {
        let stream = this.getStreamSource('parts');
        if (opus == undefined) {
            this.getRoot().subscribe(root => {
                this.rest.get(root._links.part).subscribe(data => {
                    stream.next(data);
                });
            });
        } else {
            this.rest.get(opus._links.part).subscribe(data => {
                stream.next(data);
            });
        }
        return (stream.asObservable() as Observable<ApiObject[]>);
    }

    getSubParts(): Observable<ApiObject[]> {
        let stream = this.getStreamSource('subparts');
        this.getRoot().subscribe(root => {
            this.rest.get(root._links.subpart).subscribe(data => {
                stream.next(data);
            });
        });
        return (stream.asObservable() as Observable<ApiObject[]>);
    }
}

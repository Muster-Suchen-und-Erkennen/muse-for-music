import { Injectable, OnInit } from '@angular/core';
import { Observable, } from 'rxjs/Rx';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { AsyncSubject } from 'rxjs/AsyncSubject';

export interface RootLinks extends ApiLinksObject {
    taxonomy: LinkObject;
    person: LinkObject;
    opus: LinkObject;
    part: LinkObject;
    subpart: LinkObject;
};
export interface RootModel extends ApiObject {
    _links: RootLinks;
};

@Injectable()
export class ApiService implements OnInit {

    private rootSource = new AsyncSubject<RootModel>();

    private currentRoot = this.rootSource.asObservable();

    constructor(private rest: BaseApiService) {
    }

    ngOnInit(): void {
        this.getRoot();
    }

    getRoot(): Observable<RootModel> {
        if (!this.rootSource.closed) {
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

    getTaxonomies(): Observable<Array<ApiObject>> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.taxonomy) as Observable<Array<ApiObject>>);
        });
    }

    getPeople(): Observable<Array<ApiObject>> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.person) as Observable<Array<ApiObject>>);
        });
    }

    getPerson(id: number): Observable<ApiObject> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.person.href + id) as Observable<ApiObject>);
        });
    }

    getOpuses(): Observable<Array<ApiObject>> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.opus) as Observable<Array<ApiObject>>);
        });
    }

    getParts(): Observable<Array<ApiObject>> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.part) as Observable<Array<ApiObject>>);
        });
    }

    getSubParts(): Observable<Array<ApiObject>> {
        return this.getRoot().flatMap(root => {
            return (this.rest.get(root._links.subpart) as Observable<Array<ApiObject>>);
        });
    }
}
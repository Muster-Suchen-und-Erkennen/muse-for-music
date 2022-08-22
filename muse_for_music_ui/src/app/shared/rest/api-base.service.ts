import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, AsyncSubject, throwError as observableThrowError } from 'rxjs';
import { ApiService } from './api.service';
import { catchError } from 'rxjs/operators';

export interface LinkObject {
    readonly href: string;
    readonly templated?: boolean;
}

export interface ApiLinksObject {
    readonly self: LinkObject;
    [propName: string]: LinkObject;
}

export interface ApiObject {
    readonly _links: ApiLinksObject;
    [propName: string]: any;
}

function isApiObject(toTest: any): toTest is ApiObject {
    return '_links' in toTest;
}

function isApiLinksObject(toTest: any): toTest is ApiLinksObject {
    return 'self' in toTest;
}

function isLinkObject(toTest: any): toTest is LinkObject {
    return 'href' in toTest;
}

@Injectable()
export class BaseApiService {

    // base

    private runningRequests: Map<string, AsyncSubject<unknown>> = new Map<string, AsyncSubject<unknown>>();

    constructor(private http: HttpClient) {}

    private extractUrl(url: string|LinkObject|ApiLinksObject|ApiObject): string {
        if (typeof url === 'string' || url instanceof String) {
            return (url as string);
        }
        if (isApiObject(url)) {
            url = url._links;
        }
        if (isApiLinksObject(url)) {
            url = url.self;
        }
        if (isLinkObject(url)) {
            url = url.href;
        }
        return url;
    }

    private headers(token?: string): {headers: HttpHeaders, [prop: string]: any} {
        const headers: {[prop: string]: string} = {};
        headers['Content-Type'] = 'application/json';
        if (token != null) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        return { headers: new HttpHeaders(headers) };
    }

    get<T>(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string, params?): Observable<T> {
        url = this.extractUrl(url);
        if (this.runningRequests.has(url) && params == null) {
            return this.runningRequests.get(url).asObservable() as Observable<T>;
        }
        const options = this.headers(token);
        if (params != null) {
            options.params = params;
        }

        const request = new AsyncSubject<T>();
        this.runningRequests.set(url, request);
        this.http.get<T>(url, options).pipe(
            catchError((error: any) => {
                this.runningRequests.delete(url as string);
                if (error.status != null) {
                    const message = error.error?.message ?? error.message ?? 'Server error';
                    return observableThrowError({status: error.status, message: message});
                }
                return observableThrowError(error.error ?? 'Server error');
            }),
        ).subscribe((res) => {
            request.next(res as T);
            request.complete();
            this.runningRequests.delete(url as string);
        }, (error: any) => {
                if (error.status != null) {
                    const message = error.error?.message ?? error.message ?? 'Server error';
                    return observableThrowError({status: error.status, message: message});
                } else {
                    request.error(error.error ?? 'Server error');
                }
                this.runningRequests.delete(url as string);
            });
        return request;
    }

    put<T>(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<T> {
        url = this.extractUrl(url);
        return this.http.put<T>(url, JSON.stringify(data), this.headers(token)).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    const message = error.error?.message ?? error.message ?? 'Server error';
                    return observableThrowError({status: error.status, message: message});
                }
                return observableThrowError(error.error ?? 'Server error');
            }),
        );
    }

    post<T>(url: string|LinkObject|ApiLinksObject|ApiObject, data, token?: string): Observable<T> {
        url = this.extractUrl(url);
        return this.http.post<T>(url, JSON.stringify(data), this.headers(token)).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    const message = error.error?.message ?? error.message ?? 'Server error';
                    return observableThrowError({status: error.status, message: message});
                }
                return observableThrowError(error.error ?? 'Server error');
            }),
        );
    }

    delete<T>(url: string|LinkObject|ApiLinksObject|ApiObject, token?: string, data?, params?): Observable<T> {
        url = this.extractUrl(url);
        const options = this.headers(token);
        if (data != null) {
            options.body = data;
        }
        if (params != null) {
            options.params = params;
        }
        return this.http.delete<T>(url, options).pipe(
            catchError((error: any) => {
                if (error.status != null) {
                    const message = error.error?.message ?? error.message ?? 'Server error';
                    return observableThrowError({status: error.status, message: message});
                }
                return observableThrowError(error.error ?? 'Server error');
            }),
        );
    }
}

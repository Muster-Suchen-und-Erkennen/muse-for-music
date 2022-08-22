
import {throwError as observableThrowError, timer as observableTimer,  Observable, Subject, AsyncSubject } from 'rxjs';

import {catchError, mergeMap, take} from 'rxjs/operators';
import { Injectable, OnInit, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { InfoService } from '../info/info.service';

export interface AuthRootLinks extends ApiLinksObject {
    login: LinkObject;
    fresh_login: LinkObject;
    refresh: LinkObject;
    check: LinkObject;
    management: LinkObject;
};

export interface AuthRootModel extends ApiObject {
    _links: AuthRootLinks;
    [propName: string]: any;
};

export interface ManagementRootLinks extends ApiLinksObject {
    user: LinkObject;
};

export interface ManagementRootModel extends ApiObject {
    _links: ManagementRootLinks;
    [propName: string]: any;
};

interface TokenUpdate {
    access_token: string;
    refresh_token?: string;
}

@Injectable()
export class UserApiService implements OnInit {

    private warningSet = new Set([404, 409, ]);

    private errorSet = new Set([500, 501, ]);

    private authRootSource = new AsyncSubject<AuthRootModel>();
    private currentAuthRoot = this.authRootSource.asObservable();

    private managementRootSource = new AsyncSubject<ManagementRootModel>();
    private currentManagementRoot = this.managementRootSource.asObservable();

    private streams: {[propName: string]: Subject<unknown>} = {};

    private sessionExpirySource = new Subject<boolean>();
    readonly sessionExpiry = this.sessionExpirySource.asObservable();

    private editing: boolean = true;

    readonly TOKEN = 'm4m-token';
    readonly REFRESH_TOKEN = 'm4m-refresh-token';

    constructor (private rest: BaseApiService, private info: InfoService, private router: Router) {
        observableTimer(1).pipe(take(1)).subscribe(() => {
            this.ngOnInit()
        });
    }

    ngOnInit = (): void => {
        observableTimer(1, 60000).subscribe((() => {
            if (this.loggedIn) {
                let future = new Date();
                future = new Date(future.getTime() + (3 * 60 * 1000))
                if (this.expiration(this.token) < future) {
                    this.refreshLogin(this.refreshToken);
                }
                if (this.expiration(this.refreshToken) < future) {
                    this.sessionExpirySource.next(true);
                }
            }
        }).bind(this));
    }

    updateTokens(loginToken: string, refreshToken?: string) {
        localStorage.setItem(this.TOKEN, loginToken);
        if (refreshToken != null) {
            localStorage.setItem(this.REFRESH_TOKEN, refreshToken);
        }
        if (this.router.url === '/login' && this.loggedIn) {
            this.router.navigate(['/']);
        }
    }

    logout() {
        localStorage.removeItem(this.TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
        this.router.navigate(['/login']);
    }

    get token(): string {
        return localStorage.getItem(this.TOKEN);
    }

    get refreshToken(): string {
        return localStorage.getItem(this.REFRESH_TOKEN);
    }

    private tokenToJson(token: string) {
        return JSON.parse(atob(token.split('.')[1]));
    }

    private expiration = (token: string): Date => {
        const decoded = this.tokenToJson(token);
        const exp = new Date(0);
        exp.setUTCSeconds(decoded.exp);
        return exp;
    }

    get loggedIn(): boolean {
        const token = this.refreshToken;
        return (token != null) && (this.expiration(token) > new Date());
    }

    get tokenIsActive(): boolean {
        const token = this.token;
        return (token != null) && (this.expiration(token) > new Date());
    }

    get tokenIsFresh(): boolean {
        const token = this.token;
        return (token != null) && !(!this.tokenToJson(token).fresh);
    }

    get username(): string {
        const token = this.token;
        if (token == null) {
            return undefined;
        }
        return this.tokenToJson(token).identity;
    }

    get roles(): Set<string> {
        const token = this.token;
        const roleList = this.tokenToJson(token).user_claims;
        return new Set<string>(roleList);
    }

    isEditing(): boolean {
        if (!this.loggedIn) {
            return false;
        }
        if (!this.roles.has('user') && !this.roles.has('admin')) {
            return false;
        }
        return this.editing;
    }

    toggleEditing() {
        this.editing = !this.editing;
    }

    // API Functions ///////////////////////////////////////////////////////////

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


    getAuthRoot(): Observable<AuthRootModel> {
        if (!this.authRootSource.isStopped) {
            let url = '/users'
            if ((window as any).userApiBasePath != null) {
                url = (window as any).userApiBasePath;
            }
            this.rest.get<AuthRootModel>(url).subscribe(data => {
                this.authRootSource.next(data);
                this.authRootSource.complete();
            }, error => this.errorHandler(error, 'root', 'GET'));
        }
        return this.currentAuthRoot;
    }

    login(username: string, password: string): Observable<boolean> {
        const success = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            this.rest.post<TokenUpdate>(auth._links.login, {username: username, password: password}).subscribe(data => {
                this.updateTokens(data.access_token, data.refresh_token);
                success.next(true);
                success.complete();
            }, error => {
                if (error.status === 401 ) {
                    this.info.emitWarning('Falscher Benutzername oder Passwort!', null, 5000);
                } else {
                    this.info.emitError('Mit dem Login ist irgendwas schiefgegangen.', 'Ooops', 10000);
                }
                success.next(false);
                success.complete();
            });
        });
        return success.asObservable();
    }

    refreshLogin = (refreshToken: string) => {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post<TokenUpdate>(auth._links.refresh, {}, refreshToken).subscribe(data => {
                this.updateTokens(data.access_token);
            });
        });
    }

    freshLogin = (password: string) => {
        const finished = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            this.rest.post<TokenUpdate>(auth._links.fresh_login, { username: this.username, password: password }).subscribe(data => {
                this.updateTokens(data.access_token, data.refresh_token);
                finished.next(true);
                finished.complete();
            });
        });
        return finished.asObservable()
    }

    changePassword = (password: string, passwordRepeat) => {
        const success = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links['change_password'], {
                password: password,
                password_repeat: passwordRepeat
            }, this.token).subscribe(data => {
                success.next(true);
                success.complete();
            });
        });
        return success.asObservable();
    }


    // User Management /////////////////////////////////////////////////////////

    private getStreamSource<T>(streamID: string, create: boolean = true) {
        if (this.streams[streamID] == null && create) {
            this.streams[streamID] = new Subject<T>();
        }
        return this.streams[streamID] as Subject<T>;
    }


    getManagementRoot(): Observable<ManagementRootModel> {
        return this.getAuthRoot().pipe(mergeMap(authRoot => {
            if (!this.managementRootSource.isStopped) {
                this.rest.get<ManagementRootModel>(authRoot._links.management).subscribe(data => {
                    this.managementRootSource.next(data);
                    this.managementRootSource.complete();
                }, error => this.errorHandler(error, 'root', 'GET'));
            }
            return this.currentManagementRoot;
        }))
    }

    getUsers(): Observable<ApiObject[]> {
        const resource = 'users';
        const stream = this.getStreamSource<ApiObject[]>(resource);
        this.getManagementRoot().subscribe(management => {
            this.rest.get<ApiObject[]>(management._links.user, this.token).subscribe(data => {
                stream.next(data);
            }, error => this.errorHandler(error, resource, 'GET'));
        }, error => this.errorHandler(error, resource, 'GET'));
        return stream.asObservable();
    }

    addUser(username: string, password: string): Observable<ApiObject> {
        const baseResource = 'users';
        const stream = this.getManagementRoot().pipe(
            mergeMap(management => {
                return this.rest.post<ApiObject>(management._links.user, {username: username, password: password}, this.token).pipe(
                    mergeMap(data => {
                        const stream = this.getStreamSource<ApiObject>(baseResource + '/' + data.username);
                        stream.next(data);
                        this.getUsers();
                        return stream.asObservable();
                    })
                );
            }),
            catchError(error => {
                this.errorHandler(error, baseResource, 'POST');
                return observableThrowError(error);
            }),
        );
        stream.pipe(take(1)).subscribe();
        return stream;
    }

    deleteUser(user: ApiObject, withHistory: boolean=false): void {
        const baseResource = 'users';
        const resource = baseResource + '/' + user.username;
        const stream = this.getStreamSource<ApiObject>(resource);
        this.rest.delete(user, this.token, undefined, {'with-history': withHistory}).pipe(take(1)).subscribe(data => {
            stream.next(null);
            this.getUsers();
        });
    }

    addRole(user: ApiObject, role) {
        const resource = 'users/' + user.username + '/roles';
        const stream = this.rest.post<ApiObject>(user._links.roles, role, this.token).pipe(
            mergeMap(data => {
                const stream = this.getStreamSource<ApiObject>(resource);
                stream.next(data);
                this.getUsers();
                return stream.asObservable();
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'POST');
                return observableThrowError(error);
            }),
        );
        stream.pipe(take(1)).subscribe();
        return stream;
    }

    removeRole(user: ApiObject, role) {
        const resource = 'users/' + user.username + '/roles';
        const stream = this.rest.delete<ApiObject>(user._links.roles, this.token, role).pipe(
            mergeMap(data => {
                const stream = this.getStreamSource<ApiObject>(resource);
                stream.next(data);
                this.getUsers();
                return stream.asObservable();
            }),
            catchError(error => {
                this.errorHandler(error, resource, 'DELETE');
                return observableThrowError(error);
            }),
        );
        stream.pipe(take(1)).subscribe();
        return stream;
    }

    resetPassword(user: ApiObject, password: string) {
        const baseResource = 'users';
        const resource = baseResource + '/' + user.username;
        const stream = this.getStreamSource<ApiObject>(resource);
        const success = new AsyncSubject<boolean>();
        this.rest.post<ApiObject>(user, {password: password}, this.token).subscribe(data => {
            stream.next(data);
            this.getUsers();
            success.next(true);
            success.complete();
        }, error => this.errorHandler(error, 'users/' + user.username + '/password-reset', 'POST'));
        return success.asObservable();
    }
}

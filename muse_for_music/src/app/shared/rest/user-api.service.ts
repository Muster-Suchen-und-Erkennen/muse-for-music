import { Injectable, OnInit, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { BaseApiService, ApiObject, LinkObject, ApiLinksObject } from './api-base.service';
import { InfoService } from '../info/info.service';
import { Observable, } from 'rxjs/Rx';
import { AsyncSubject } from 'rxjs/AsyncSubject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

export interface AuthRootLinks extends ApiLinksObject {
    login: LinkObject;
    fresh_login: LinkObject;
    refresh: LinkObject;
    check: LinkObject;
};

export interface AuthRootModel extends ApiObject {
    _links: AuthRootLinks;
    [propName: string]: any;
};

@Injectable()
export class UserApiService implements OnInit {

    private warningSet = new Set([404, 409, ]);

    private errorSet = new Set([500, 501, ]);

    private authRootSource = new AsyncSubject<AuthRootModel>();

    private currentAuthRoot = this.authRootSource.asObservable();

    readonly TOKEN = 'token';
    readonly REFRESH_TOKEN = 'refresh_token';

    constructor (private rest: BaseApiService, private info: InfoService, private router: Router) {
        Observable.timer(1).take(1).subscribe(() => {
            this.ngOnInit()
        });
    }

    ngOnInit = (): void => {
        Observable.timer(1, 60000).subscribe((() => {
            if (this.loggedIn) {
                let future = new Date();
                future = new Date(future.getTime() + (3 * 60 * 1000))
                if (this.expiration(this.token) < future) {
                    this.refreshLogin(this.refreshToken);
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

    // API Functions ///////////////////////////////////////////////////////////

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


    getAuthRoot(): Observable<AuthRootModel> {
        if (!this.authRootSource.isStopped) {
            let url = '/users'
            if ((window as any).userApiBasePath != null) {
                url = (window as any).userApiBasePath;
            }
            console.log(url);
            this.rest.get(url).subscribe(data => {
                this.authRootSource.next((data as AuthRootModel));
                this.authRootSource.complete();
            }, error => this.errorHandler(error, 'root', 'GET'));
        }
        return this.currentAuthRoot;
    }

    login(username: string, password: string): Observable<boolean> {
        const success = new AsyncSubject<boolean>();
        this.getAuthRoot().subscribe(auth => {
            console.log(auth._links.login)
            this.rest.post(auth._links.login, {username: username, password: password}).subscribe(data => {
                this.updateTokens(data.access_token, data.refresh_token);
                success.next(true);
                success.complete();
            }, error => {
                if (error.status === 401 ) {
                    this.info.emitWarning('Wrong username or password!', null, 5000);
                } else {
                    this.info.emitError('Something went wrong with that login. Please try again.', 'Ooops', 10000);
                }
                success.next(false);
                success.complete();
            });
        });
        return success.asObservable();
    }

    guestLogin() {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.guest_login, {}).subscribe(data => {
                this.updateTokens(data.access_token, data.refresh_token);
            });
        });
    }

    refreshLogin = (refreshToken: string) => {
        this.getAuthRoot().subscribe(auth => {
            this.rest.post(auth._links.refresh, {}, refreshToken).subscribe(data => {
                this.updateTokens(data.access_token);
            });
        });
    }
}

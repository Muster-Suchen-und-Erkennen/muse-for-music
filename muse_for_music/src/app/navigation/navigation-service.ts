import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { list } from 'postcss';

export class Breadcrumb {

    readonly title: string;
    readonly target: string;

    constructor(title: string, target: string) {
        this.title = title;
        this.target = target;
    }

}

@Injectable()
export class NavigationService {

    private titleSource = new BehaviorSubject<string>('MUSE4Music');
    private breadcrumSource = new BehaviorSubject<Array<Breadcrumb>>([]);

    currentTitle = this.titleSource.asObservable();
    currentBreadcrumbs = this.breadcrumSource.asObservable();

    constructor() { }

    changeTitle(newTitle: string) {
        this.titleSource.next(newTitle);
    }

    changeBreadcrumbs(newBreadcrumbs: Array<Breadcrumb>) {
        this.breadcrumSource.next(newBreadcrumbs);
    }

}

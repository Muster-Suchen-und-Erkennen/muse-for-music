
import { Subscription, timer } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { NavigationService, Breadcrumb } from './navigation-service';


@Component({
  selector: 'm4m-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit, OnDestroy {

    @ViewChild('home', {static: true}) home: ElementRef;
    @ViewChild('bcContainer') bcContainer: ElementRef;

    hovered: boolean = false;

    breadcrumbs: Array<Breadcrumb>;

    private sub: Subscription|null=null;

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.sub = this.data.currentBreadcrumbs.subscribe(breadcrumbs => {
            this.breadcrumbs = breadcrumbs;
            this.scrollToBottom();
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    breadcrumbHeight = () => {
        return this.home?.nativeElement?.offsetHeight ?? 1;
    }

    scrollToBottom = () => {
        timer(50).pipe(take(1)).subscribe(() => {
            const element = this.bcContainer?.nativeElement;
            if (element != null) {
                element.scrollTop = element.scrollHeight;
            }
        });
    }

}

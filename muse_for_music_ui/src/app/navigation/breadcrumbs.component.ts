
import { timer } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { NavigationService, Breadcrumb } from './navigation-service';


@Component({
  selector: 'm4m-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit {

    @ViewChild('home', {static: true}) home: ElementRef;
    @ViewChild('bcContainer') bcContainer: ElementRef;

    hovered: boolean = false;

    breadcrumbs: Array<Breadcrumb>;

    constructor(private data: NavigationService) { }

    ngOnInit(): void {
        this.data.currentBreadcrumbs.subscribe(breadcrumbs => {
            this.breadcrumbs = breadcrumbs;
            this.scrollToBottom();
        });
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

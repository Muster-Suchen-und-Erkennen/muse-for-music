
import {timer as observableTimer,  Observable, Subscription, } from 'rxjs';

import {take} from 'rxjs/operators';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { InfoService, Message } from './info.service';


@Component({
  selector: 'm4m-info',
  templateUrl: './info.component.html'
})
export class InfoComponent implements OnInit, OnDestroy {

    messages: Array<Message>;

    private sub: Subscription|null = null;

    constructor(private info: InfoService) { }

    ngOnInit(): void {
        this.messages = [];
        this.sub = this.info.messages.subscribe(message => this.addMessage(message));
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    addMessage(message: Message) {
        this.messages.push(message);
        if (message.timeout != null && message.timeout > 0) {
            observableTimer(message.timeout).pipe(take(1)).subscribe((() => this.remove(message)).bind(this));
        }
    }

    remove(message: Message) {
        const index = this.messages.findIndex(value => value.createdAt === message.createdAt);
        this.messages.splice(index, 1);
    }

}

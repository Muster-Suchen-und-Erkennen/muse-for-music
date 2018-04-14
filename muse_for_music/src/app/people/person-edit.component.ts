import { Component, OnInit, OnChanges, SimpleChanges, Input, OnDestroy, ViewChild } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { Subscription } from 'rxjs/Rx';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';

@Component({
  selector: 'm4m-person-edit',
  templateUrl: './person-edit.component.html',
  styleUrls: ['./person-edit.component.scss']
})
export class PersonEditComponent implements OnInit, OnChanges, OnDestroy {

    private subscription: Subscription;

    @ViewChild(DynamicFormComponent) form;

    @Input() personID: number;
    person: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    constructor(private api: ApiService) { }

    update() {
        this.unsubscribe();
        this.subscription = this.api.getPerson(this.personID).subscribe(data => {
            if (data != undefined) {
                this.person = data;
            }
        });
    }

    unsubscribe() {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }
    }

    ngOnInit(): void {
        this.update();
    }

    ngOnChanges(changes: SimpleChanges): void {
        this.update();
    }

    ngOnDestroy(): void {
        this.unsubscribe();
    }

    save = (event) => {
        this.api.putPerson(this.personID, event).take(1).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deletePerson(this.person);
    };

}

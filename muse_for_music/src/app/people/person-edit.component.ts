import { Component, OnInit, OnChanges, SimpleChanges, Input, OnDestroy } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'm4m-person-edit',
  templateUrl: './person-edit.component.html',
  styleUrls: ['./person-edit.component.scss']
})
export class PersonEditComponent implements OnInit, OnChanges, OnDestroy {

    private subscription: Subscription;

    @Input() personID: number;
    person: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    valid: boolean = false;
    data: any = {};

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

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    save(event) {
        if (this.valid) {
            this.api.putPerson(this.personID, this.data);
        }
    }

    delete = (() => {
        this.api.deletePerson(this.person);
    }).bind(this);

}

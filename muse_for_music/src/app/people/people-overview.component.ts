import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'm4m-people-overview',
  templateUrl: './people-overview.component.html',
  styleUrls: ['./people-overview.component.scss']
})
export class PeopleOverviewComponent implements OnInit {

    persons: Array<ApiObject>;
    selected: number = 1;

    swagger: any;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('MUSE4Music – People');
        this.data.changeBreadcrumbs([new Breadcrumb('People', '/people')]);
        this.api.getPeople().subscribe(data => this.persons = data);
    }

    newPerson(event) {
        this.api.postPerson({
            "name": "NEW",
            "gender": "other"
          }).subscribe(person => {
            this.selected = person.id;
        });
    }

    selectPerson(event, person: ApiObject) {
        this.selected = person.id;
    }

}

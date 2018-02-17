import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';

@Component({
  selector: 'm4m-people-overview',
  templateUrl: './people-overview.component.html',
  styleUrls: ['./people-overview.component.scss']
})
export class PeopleOverviewComponent implements OnInit {

    persons: Array<ApiObject>;
    tableData: TableRow[];
    selected: number = 1;

    swagger: any;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('MUSE4Music – People');
        this.data.changeBreadcrumbs([new Breadcrumb('People', '/people')]);
        this.api.getPeople().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.persons = data;
            const tableData = [];
            this.persons.forEach(person => {
                const row = new TableRow(person.id, [person.name, person.gender, person.birth_date + ' – ' + person.death_date]);
                tableData.push(row);
            });
            this.tableData = tableData;
        });
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

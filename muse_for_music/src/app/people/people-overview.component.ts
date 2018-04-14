import { Component, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';

@Component({
  selector: 'm4m-people-overview',
  templateUrl: './people-overview.component.html',
  styleUrls: ['./people-overview.component.scss'],
  providers: [DatePipe]
})
export class PeopleOverviewComponent implements OnInit {

    persons: Array<ApiObject>;
    tableData: TableRow[];
    selected: number = 1;

    swagger: any;

    constructor(private data: NavigationService, private api: ApiService, private datePipe: DatePipe) { }

    ngOnInit(): void {
        this.data.changeTitle('MUSE4Music – People');
        this.data.changeBreadcrumbs([new Breadcrumb('People', '/people')]);
        this.api.getPeople().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.persons = data;
            const tableData = [];
            let selected;
            this.persons.forEach(person => {
                if (this.selected !== selected) {
                    selected = person.id;
                }
                let birth = this.datePipe.transform(person.birth_date, 'mediumDate') + ' *';
                let death = this.datePipe.transform(person.death_date, 'mediumDate') + ' ✝';
                if (person.birth_date === '0001-01-01') {
                    birth = 'na';
                }
                if (person.death_date === '0001-01-01') {
                    death = 'na';
                }
                const row = new TableRow(person.id, [person.name, person.gender,
                    birth + ' – ' + death]);
                tableData.push(row);
            });
            this.selected = selected;
            this.tableData = tableData;
        });
    }

    newPerson(event) {
        this.api.postPerson({
            "name": "NEW",
            "gender": "other"
          }).take(1).subscribe(person => {
            this.selected = person.id;
        });
    }

    selectPerson(event, person: ApiObject) {
        this.selected = person.id;
    }

}

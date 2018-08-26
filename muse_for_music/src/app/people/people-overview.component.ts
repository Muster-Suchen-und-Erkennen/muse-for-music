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

    valid: boolean;
    newPersonData: any;

    persons: Array<ApiObject>;
    tableData: TableRow[];
    selected: number;

    swagger: any;

    constructor(private data: NavigationService, private api: ApiService, private datePipe: DatePipe) { }

    ngOnInit(): void {
        this.data.changeTitle('Personen');
        this.data.changeBreadcrumbs([new Breadcrumb('Personen', '/people')]);
        this.api.getPeople().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.persons = data;
            const tableData = [];
            let selected;
            this.persons.forEach(person => {
                if (this.selected == null || this.selected !== selected) {
                    selected = person.id;
                }
                let birth = this.formatDate(person.birth_date) + ' *';
                let death = this.formatDate(person.death_date) + ' ✝';
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

    formatDate(date: string): string {
        if (date.match(/[0-9]{4}-[0-9]{2}-[0-9]{2}/)) {
            const parts = date.split('-');
            return parts[2] + '.' + parts[1] + '.' + parts[0];
        } else {
            return date;
        }
    }

    save = () => {
        if (this.valid) {
            this.api.postPerson(this.newPersonData).subscribe(person => {
                this.selected = person.id;
            });
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newPersonData = data;
    }

    selectPerson(event, person: ApiObject) {
        this.selected = person.id;
    }

}

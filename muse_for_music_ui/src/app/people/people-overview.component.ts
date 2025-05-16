import { Component, OnDestroy, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';
import { Subscription } from 'rxjs';
import { take } from 'rxjs/operators';

@Component({
  selector: 'm4m-people-overview',
  templateUrl: './people-overview.component.html',
  styleUrls: ['./people-overview.component.scss'],
  providers: [DatePipe]
})
export class PeopleOverviewComponent implements OnInit, OnDestroy {

    valid: boolean;
    newPersonData: any;

    persons: Array<ApiObject>;
    tableData: TableRow[];
    selected: number;
    selectedPerson: ApiObject;

    swagger: any;

    private sub: Subscription|null = null;

    constructor(private data: NavigationService, private api: ApiService, private userApi: UserApiService, private datePipe: DatePipe) { }

    ngOnInit(): void {
        this.data.changeTitle('Personen');
        this.data.changeBreadcrumbs([new Breadcrumb('Personen', '/people')]);
        this.sub = this.api.getPeople().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.persons = data;
            const tableData = [];
            let selected;
            let selectedPerson;
            this.persons.forEach(person => {
                if (this.selected == null || this.selected !== selected) {
                    selected = person.id;
                    selectedPerson = person;
                }
                let birth = person.birth_date + ' *';
                let death = person.death_date + ' ✝';
                if (person.birth_date < 0) {
                    birth = 'na';
                }
                if (person.death_date < 0) {
                    death = 'na';
                }
                const row = new TableRow(person.id, [person.name, person.gender,
                    birth + ' – ' + death]);
                tableData.push(row);
            });
            this.selected = selected;
            this.selectedPerson = selectedPerson;
            this.tableData = tableData;
        });
    }

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    save = () => {
        if (this.valid) {
            this.api.postPerson(this.newPersonData).pipe(take(1)).subscribe(person => {
                this.selected = person.id;
                this.selectedPerson = person;
            });
        }
    };

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newPersonData = data;
    }

    selectPerson(event, person: ApiObject) {
        this.selected = person.id;
        this.selectedPerson = person;
    }

}

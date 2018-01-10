import { Component, OnInit } from '@angular/core';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'm4m-opuses-overview',
  templateUrl: './opuses-overview.component.html',
  styleUrls: ['./opuses-overview.component.scss']
})
export class OpusesOverviewComponent implements OnInit {

    opuses: Array<ApiObject>;

    swagger: any;

    constructor(private data: NavigationService, private api: ApiService) { }

    ngOnInit(): void {
        this.data.changeTitle('MUSE4Music – Opuses');
        this.data.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses')]);
        this.api.getOpuses().subscribe(data => this.opuses = data);
    }

    newOpus(event) {
        //this.api.postPerson({
        //    "name": "NEW",
        //    "gender": "other"
        //  }).subscribe(person => {
        //    this.selected = person.id;
        //});
    }

}

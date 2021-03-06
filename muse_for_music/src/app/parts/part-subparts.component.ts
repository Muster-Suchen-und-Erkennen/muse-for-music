import { Component, OnInit, Input, Testability } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';

@Component({
  selector: 'm4m-part-subparts',
  templateUrl: './part-subparts.component.html',
  styleUrls: ['./part-subparts.component.scss']
})
export class PartSubpartsComponent implements OnInit {

    @Input() partID: number;

    part: ApiObject;
    subparts: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newSubPartData: any;

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.api.getPart(this.partID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.part = data;
            this.subparts = this.part.subparts;
            this.api.getSubParts(data).subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.subparts = data;
                const tableData = [];
                this.subparts.forEach(subpart => {
                    const row = new TableRow(subpart.id, [subpart.label],
                                             ['subparts', subpart.id]);
                    tableData.push(row);
                });
                this.tableData = tableData;
            });
        });
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }


    save = () => {
        if (this.valid) {
            this.api.postSubPart(this.part, this.newSubPartData).subscribe(_ => {return});
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newSubPartData = data;
    }
}

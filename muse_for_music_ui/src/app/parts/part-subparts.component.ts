import { Component, OnInit, Input, Testability, OnDestroy } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';
import { Subscription } from 'rxjs';
import { take } from 'rxjs/operators';

@Component({
  selector: 'm4m-part-subparts',
  templateUrl: './part-subparts.component.html',
  styleUrls: ['./part-subparts.component.scss']
})
export class PartSubpartsComponent implements OnInit, OnDestroy {

    @Input() partID: number;

    part: ApiObject;
    subparts: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newSubPartData: any;

    private partSub: Subscription|null = null;
    private subPartSub: Subscription|null = null;

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.partSub = this.api.getPart(this.partID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.part = data;
            this.subparts = this.part.subparts;
            if (this.subPartSub != null) {
                this.subPartSub.unsubscribe();
            }
            this.subPartSub = this.api.getSubParts(data).subscribe(data => {
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

    ngOnDestroy(): void {
        if (this.partSub != null) {
            this.partSub.unsubscribe();
        }
        if (this.subPartSub != null) {
            this.subPartSub.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }


    save = () => {
        if (this.valid) {
            this.api.postSubPart(this.part, this.newSubPartData).pipe(take(1)).subscribe(_ => {return});
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newSubPartData = data;
    }
}

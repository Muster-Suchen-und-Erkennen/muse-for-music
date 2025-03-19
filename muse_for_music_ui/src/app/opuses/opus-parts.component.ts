import { Component, OnInit, Input, Testability, OnDestroy } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';
import { Subscription } from 'rxjs';
import { take } from 'rxjs/operators';

@Component({
  selector: 'm4m-opus-parts',
  templateUrl: './opus-parts.component.html',
  styleUrls: ['./opus-parts.component.scss']
})
export class OpusPartsComponent implements OnInit, OnDestroy {

    @Input() opusID: number;

    opus: ApiObject;
    parts: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newPartData: any;

    private opusSub: Subscription|null = null;
    private partsSub: Subscription|null = null;

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.opusSub = this.api.getOpus(this.opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opus = data;
            this.parts = this.opus.parts;
            if (this.partsSub != null) {
                this.partsSub.unsubscribe();
            }
            this.partsSub = this.api.getParts(data).subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.parts = data;
                const tableData = [];
                this.parts.forEach(part => {
                    const row = new TableRow(part.id, [part.measure_start.measure, part.measure_end.measure, part.length, [part.name]],
                                             ['parts', part.id]);
                    tableData.push(row);
                });
                this.tableData = tableData;
            });
        });
    }

    ngOnDestroy(): void {
        if (this.opusSub != null) {
            this.opusSub.unsubscribe();
        }
        if (this.partsSub != null) {
            this.partsSub.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }

    save = () => {
        if (this.valid) {
            this.api.postPart(this.opus, this.newPartData).pipe(take(1)).subscribe(_ => {return});
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newPartData = data;
    }
}

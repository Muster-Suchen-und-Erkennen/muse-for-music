import { Component, OnInit, Input, Testability } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';

@Component({
  selector: 'm4m-opus-parts',
  templateUrl: './opus-parts.component.html',
  styleUrls: ['./opus-parts.component.scss']
})
export class OpusPartsComponent implements OnInit {

    @Input() opusID: number;

    opus: ApiObject;
    parts: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newPartData: any;

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.api.getOpus(this.opusID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opus = data;
            this.parts = this.opus.parts;
            this.api.getParts(data).subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.parts = data;
                const tableData = [];
                this.parts.forEach(part => {
                    const row = new TableRow(part.id, [part.measure_start.measure, part.measure_end.measure, part.length],
                                             ['parts', part.id]);
                    tableData.push(row);
                });
                this.tableData = tableData;
            });
        });
    }

    save = (() => {
        if (this.valid) {
            this.api.postPart(this.opus, this.newPartData).subscribe(_ => {return});
        }
    }).bind(this);

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newPartData = data;
    }
}

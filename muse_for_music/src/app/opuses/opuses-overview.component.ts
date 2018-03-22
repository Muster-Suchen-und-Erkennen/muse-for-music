import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';

@Component({
  selector: 'm4m-opuses-overview',
  templateUrl: './opuses-overview.component.html',
  styleUrls: ['./opuses-overview.component.scss']
})
export class OpusesOverviewComponent implements OnInit {

    opuses: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newOpusData: any;

    constructor(private data: NavigationService, private api: ApiService, private router: Router, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('MUSE4Music – Opuses');
        this.data.changeBreadcrumbs([new Breadcrumb('Opuses', '/opuses')]);
        this.api.getOpuses().subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.opuses = data;
            const tableData = [];
            this.opuses.forEach(opus => {
                const row = new TableRow(opus.id, [opus.name, opus.genre.name, opus.composer.name], [opus.id], true);
                tableData.push(row);
            });
            this.tableData = tableData;
        });
    }

    save = (() => {
        if (this.valid) {
            this.api.postOpus(this.newOpusData).subscribe(data => {
                this.router.navigate([data.id], {relativeTo: this.route});
            });
        }
    }).bind(this);

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newOpusData = data;
    }
}

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';
import { take } from 'rxjs/operators';
import { Subscription } from 'rxjs';

@Component({
  selector: 'm4m-opuses-overview',
  templateUrl: './opuses-overview.component.html',
  styleUrls: ['./opuses-overview.component.scss']
})
export class OpusesOverviewComponent implements OnInit, OnDestroy {

    opuses: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean = false;

    newOpusData: any;

    private sub: Subscription|null = null;

    constructor(private data: NavigationService, private api: ApiService, private userApi: UserApiService, private router: Router, private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.data.changeTitle('Werke');
        this.data.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses')]);
        this.sub = this.api.getOpuses().subscribe(data => {
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

    ngOnDestroy(): void {
        if (this.sub != null) {
            this.sub.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }

    save = () => {
        if (this.valid) {
            this.api.postOpus(this.newOpusData).pipe(take(1)).subscribe(data => {
                this.router.navigate([data.id], {relativeTo: this.route});
            });
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newOpusData = data;
    }
}

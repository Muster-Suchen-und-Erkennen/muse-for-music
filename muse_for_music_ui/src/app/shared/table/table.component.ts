import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

export class TableRow {

    id: number;
    route?: (string | number)[];
    routeRelative?: boolean;
    content: string[];

    constructor(id: number, content: string[], route?: (string | number)[], routeRelative?: boolean) {
        this.id = id;
        this.content = content;
        this.route = route;
        this.routeRelative = routeRelative;
    }
}

@Component({
    selector: 'm4m-table',
    templateUrl: './table.component.html',
    styleUrls: ['./table.component.scss']
})
export class myTableComponent implements OnChanges {

    @Input() selected: number;
    @Input() headings: string[];
    @Input() rows: TableRow[];

    @Output() selectedChange = new EventEmitter();

    @Input() sortByColumn: number;
    @Input() sortAscending: boolean = true;

    order: number[];

    constructor(private router: Router, private route: ActivatedRoute){}

    ngOnChanges() {
        const order = [];
        if (this.rows != null) {
            this.rows.forEach((row, index) => order.push(index));
        }
        this.order = order;
        this.sort();
    }

    sort() {
        this.order.sort((a, b) => {
            if (this.sortByColumn == null || this.sortByColumn < 0 || this.sortByColumn >= this.headings.length) {
                if (this.sortAscending) {
                    return a - b;
                } else {
                    return b - a;
                }
            }
            const rowA = this.rows[a];
            const rowB = this.rows[b];
            if (rowA.content[this.sortByColumn] > rowB.content[this.sortByColumn]) {
                return this.sortAscending ? 1 : -1;
            }
            if (rowA.content[this.sortByColumn] == rowB.content[this.sortByColumn]) {
                return 0;
            }
            if (rowA.content[this.sortByColumn] < rowB.content[this.sortByColumn]) {
                return this.sortAscending ? -1 : 1;
            }
        });
    }

    changeSorting(column: number) {
        if (this.sortByColumn === column || column == null) {
            if (!this.sortAscending) {
                this.sortByColumn = null;
            }
            this.sortAscending = !this.sortAscending;
        } else {
            this.sortByColumn = column;
            this.sortAscending = true;
        }
        this.sort();
    }

    selectRow(row: TableRow) {
        if (row.route != undefined) {
            if (row.routeRelative) {
                this.router.navigate(row.route, {relativeTo: this.route});
            } else {
                this.router.navigate(row.route);
            }
        } else {
            this.selectedChange.emit(row.id);
        }
    }
}

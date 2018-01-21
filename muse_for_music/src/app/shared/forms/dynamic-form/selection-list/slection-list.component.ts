import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
    selector: 'm4m-selection-list',
    templateUrl: './selection-list.component.html',
    styleUrls: ['./selection-list.component.scss']
})
export class SelectionListComponent implements OnChanges {

    @Input() selectables: any[];
    @Input() display: string;

    @Input() search: string;
    @Input() selected: number;

    highlighted: number = 0;
    matching: Set<number> = new Set<number>();

    ngOnChanges(changes: SimpleChanges): void {
        this.updateMatching();
    }

    updateMatching () {
        if (this.selectables == undefined || this.display == undefined) {
            return;
        }
        if (this.search == undefined) {
            this.search = '';
        }
        let searchString = this.search.toUpperCase();
        let matches = new Set<number>();
        for (let index in this.selectables) {
            if (this.selectables[index][this.display].toString().toUpperCase().includes(searchString)){
                matches.add(parseInt(index));
            }
        }
        if (matches.size > 0) {
            if (! matches.has(this.highlighted)) {
                this.highlighted = matches.values[0];
            }
        }
        this.matching = matches;
    }
}

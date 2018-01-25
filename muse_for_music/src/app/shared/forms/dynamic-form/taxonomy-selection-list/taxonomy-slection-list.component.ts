import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, OnInit } from '@angular/core';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

class TaxonomyItem {
    id: number;
    name: string;
    description?: string;
    data: any;
    depth?: number;
    children?: TaxonomyItem[];

    constructor(data: any, depth?: number) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description;
        this.data = data;
        this.depth = 0;
        this.children = [];
        if (depth != undefined) {
            this.depth = depth;
        }
    }
}


@Component({
    selector: 'm4m-taxonomy-selection-list',
    templateUrl: './taxonomy-selection-list.component.html',
    styleUrls: ['./taxonomy-selection-list.component.scss']
})
export class TaxonomySelectionListComponent implements OnChanges, OnInit {

    isTree: boolean;

    selectables: TaxonomyItem[];

    @Input() taxonomy: string;
    @Input() allowedSelections: number = 0;

    @Input() search: string;
    @Input() _selected: any[];
    @Output() selectedChange = new EventEmitter();

    highlighted: number = undefined;
    selectedSet: Set<number> = new Set<number>();
    matching: Set<number> = new Set<number>();
    openNodes: Set<number> = new Set<number>();

    get selected(): any[] {
        let selected = [];
        for (let item of this.selectables) {
            if (this.selectedSet.has(item.id)) {
                selected.push(item.data);
            }
        }
        return selected;
    }

    set selected(selection: any[]) {
        let selected = new Set<number>();
        for (let item of selection) {
            selected.add(item.id);
        }
        this.selectedSet = selected;
    }

    constructor(private api: ApiService) {}

    ngOnChanges(changes: SimpleChanges): void {
        this.updateMatching();
    }

    ngOnInit(): void {
        this.api.getTaxonomy(this.taxonomy).subscribe(taxonomy => {
            if (taxonomy == undefined) {
                return;
            }
            if (taxonomy.taxonomy_type === 'tree') {
                this.isTree = true;
                this.prepareTreeTaxonomy(taxonomy.items);
            } else {
                this.isTree = false;
                this.prepareListTaxonomy(taxonomy.items);
            }
            this.updateMatching();
        });
    }

    prepareListTaxonomy(items) {
        let selectables = [];
        for (let item of items) {
            selectables.push(new TaxonomyItem(item));
        }
        this.selectables = selectables;
    }

    prepareTreeTaxonomy(item, flatList?: TaxonomyItem[], parents?: Set<TaxonomyItem>) {
        let recursionStart = false;
        if (parents == undefined) {
            parents = new Set<TaxonomyItem>();
        }
        if (flatList == undefined) {
            flatList = [];
            recursionStart = true;
        }
        let children = item.children;
        item.children = [];

        let node = new TaxonomyItem(item, parents.size);
        flatList.push(node);
        parents.add(node);
        for (let child of children) {
            this.prepareTreeTaxonomy(child, flatList, parents);
        }
        parents.delete(node);

        if (recursionStart) {
            this.selectables = flatList;
        }
    }

    updateMatching() {
        if (this.selectables == undefined) {
            return;
        }
        if (this.search == undefined) {
            this.search = '';
        }
        let searchString = this.search.toUpperCase();
        let matches = new Set<number>();

        for (let item of this.selectables) {
            if (item.name.toUpperCase().includes(searchString) ||
                item.description.toUpperCase().includes(searchString)) {
                matches.add(item.id);
            }
        }
        this.matching = matches;
    }

    deselect(key?: any) {
        if (key == undefined) {
            return;
        }
        this.selectedSet.delete(key);
        this.selectedChange.emit(this.selected);
    }

    select(key?: any) {
        if (key == undefined) {
            key = this.highlighted;
        }
        if (key == undefined) {
            return;
        }
        if (this.selectedSet.has(key)) {
            this.selectedSet.delete(key);
        } else {
            if (this.allowedSelections === 1) {
                this.selectedSet.clear();
            }
            if (this.allowedSelections === -1 || this.selectedSet.size < this.allowedSelections) {
                this.selectedSet.add(key);
            }
        }
        this.selectedChange.emit(this.selected);
    }

    highlightNext() {
    }

    highlightPrevious() {
    }
}

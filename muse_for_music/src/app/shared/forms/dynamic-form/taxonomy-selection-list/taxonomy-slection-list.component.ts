import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, OnInit } from '@angular/core';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

class TaxonomyItem {
    id: number;
    name: string;
    description?: string;
    data: any;
    depth: number;
    parents: number[];
    children: number[];

    constructor(data: any, depth?: number) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description;
        this.data = data;
        this.depth = 0;
        this.parents = [];
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
    filter: boolean = true;
    showTree: boolean = false;

    selectables: TaxonomyItem[];

    @Input() taxonomy: string;
    @Input() allowedSelections: number = 0;

    @Input() search: string;
    @Input() _selected: any[];
    @Output() selectedChange = new EventEmitter();

    highlightable: number[] = [];
    closed: Set<number> = new Set<number>();

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

    visible(selectable: TaxonomyItem): boolean {
        if (!this.filter) {
            return true;
        }
        if (this.showTree) {
            for (let parent of selectable.parents) {
                if (this.closed.has(parent)) {
                    return false;
                }
            }
            if (this.matching.has(selectable.id)) {
                return true;
            }
            for (let child of selectable.children) {
                if (this.matching.has(child)) {
                    return true;
                }
            }
            return false;
        } else {
            return this.matching.has(selectable.id);
        }
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
                this.showTree = true;
                this.prepareTreeTaxonomy(taxonomy.items);
            } else {
                this.isTree = false;
                this.showTree = false;
                this.prepareListTaxonomy(taxonomy.items);
            }
            this.closed.clear();
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

        parents.forEach(parent => {
            parent.children.push(node.id);
            node.parents.push(parent.id);
        });

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
                item.description.toUpperCase().includes(searchString) ||
                (item.name === 'root' && this.taxonomy.toUpperCase().includes(searchString))) {
                matches.add(item.id);
            }
        }
        this.matching = matches;
        this.updateHighlightable();
    }

    updateHighlightable() {
        let items: number[] = [];
        let highlightedStillValid = false;
        for (let item of this.selectables) {
            if (!this.filter || this.matching.has(item.id)) {
                if (this.showTree) {
                    if (this.visible(item)) {
                        items.push(item.id);
                        if (item.id === this.highlighted) {
                            highlightedStillValid = true;
                        }
                    }
                } else {
                    items.push(item.id);
                    if (item.id === this.highlighted) {
                        highlightedStillValid = true;
                    }
                }
            }
        }

        this.highlightable = items;

        if (!highlightedStillValid && items.length > 0) {
            this.highlighted = items[0];
        }
    }

    toggleClosed(selectable: TaxonomyItem) {
        if (selectable.children.length > 0) {
            if (this.closed.has(selectable.id)) {
                this.closed.delete(selectable.id);
            } else {
                this.closed.add(selectable.id);
            }
        }
        this.updateHighlightable();
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
        let searching = true;
        for (let key of this.highlightable) {
            if (searching && key === this.highlighted){
                searching = false;
                continue;
            }
            if (!searching) {
                this.highlighted = key;
                return;
            }
        }
    }

    highlightPrevious() {
        let previous: number = this.highlighted;
        for (let key of this.highlightable) {
            if (key === this.highlighted){
                this.highlighted = previous;
                return;
            }
            previous = key;
        }
    }
}

import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, OnInit } from '@angular/core';

import { ApiObject } from '../../../rest/api-base.service';
import { ApiService } from '../../../rest/api.service';

class Selectable {
    id: number;
    name: string;
    data: any;

    constructor(data: any, display: string, key: string) {
        this.name = data[display];
        this.id = data[key];
        this.data = data;
    }
}


@Component({
    selector: 'm4m-selection-list',
    templateUrl: './selection-list.component.html',
    styleUrls: ['./selection-list.component.scss']
})
export class SelectionListComponent implements OnChanges {

    filter: boolean = true;

    _selectables: Selectable[] = [];

    @Input() display: string = 'id';
    @Input() key: string = 'id';
    @Input() allowedSelections: number = 0;
    @Input() createNewIfNoMatch: boolean = false;

    @Input() search: string;
    @Output() selectedChange = new EventEmitter();
    @Output() createNew = new EventEmitter();

    highlightable: number[] = [];

    highlighted: number = undefined;
    selectedSet: Set<number> = new Set<number>();
    matching: Set<number> = new Set<number>();

    selectableId(index, selectable) {
        return selectable.id;
    }

    @Input()
    set selected(selection: any[]) {
        const selected = new Set<number>();
        for (const item of selection) {
            selected.add(item.id);
        }

        this.selectedSet = selected;
    }

    get selected(): any[] {
        const selectedList = [];
        const selectables = this._selectables;
        for (const item of selectables) {
            if (this.selectedSet.has(item.id)) {
                selectedList.push(item.data);
            }
        }
        return selectedList;
    }

    @Input()
    set selectables(selectables: any[]) {
        if (selectables == null) {
            selectables = [];
        }
        const selectablesList = [];
        for (const item of selectables) {
            selectablesList.push(new Selectable(item, this.display, this.key));
        }
        this._selectables = selectablesList;
        this.updateMatching(this.search);
    }

    get selectables(): any[] {
        if (this._selectables != null) {
            const selectables = [];
            for (const item of this._selectables) {
                selectables.push(item.data);
            }
            return selectables;
        }
        return [];
    }

    visible(selectable: Selectable): boolean {
        if (!this.filter) {
            return true;
        }
        return this.matching.has(selectable.id);
    }

    constructor(private api: ApiService) { }

    ngOnChanges(changes: SimpleChanges): void {
        this.updateMatching(this.search);
        // https://stackoverflow.com/questions/42819549/angular2-scroll-to-element-that-has-ngif
    }

    updateMatching(searchString: string) {
        if (this._selectables == null) {
            return;
        }
        if (searchString == null) {
                searchString = '';
        }
        searchString = searchString.toUpperCase();
        const matches = new Set<number>();

        for (const item of this._selectables) {
            if (item.name.toString().toUpperCase().includes(searchString)) {
                matches.add(item.id);
            }
        }
        this.matching = matches;
        this.updateHighlightable();
    }

    updateHighlightable() {
        const items: number[] = [];
        let highlightedStillValid = false;
        for (const item of this._selectables) {
            if (!this.filter || this.matching.has(item.id)) {
                items.push(item.id);
                if (item.id === this.highlighted) {
                    highlightedStillValid = true;
                }
            }
        }

        this.highlightable = items;

        if (!highlightedStillValid && items.length > 0) {
            this.highlighted = items[0];
        }
    }

    toggleClosed(selectable: Selectable) {
        this.updateHighlightable();
    }

    deselect(key?: any) {
        if (key == null) {
            return;
        }
        this.selectedSet.delete(key);
        this.selectedChange.emit(this.selected);
    }

    select(key?: any) {
        if (key == null && this.createNewIfNoMatch && this.matching.size === 0) {
            this.updateMatching('');
            const newObject = {};
            newObject[this.display] = this.search;
            this.createNew.emit(newObject);
            return
        }
        if (key == null) {
            key = this.highlighted;
        }
        if (key == null) {
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
        for (const key of this.highlightable) {
            if (searching && key === this.highlighted) {
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
        for (const key of this.highlightable) {
            if (key === this.highlighted) {
                this.highlighted = previous;
                return;
            }
            previous = key;
        }
    }
}

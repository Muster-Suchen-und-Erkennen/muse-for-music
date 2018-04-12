import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';

class Selectable {
    label: string;
    id: string|number;
    data: any;

    constructor(data: any, display: string, key: string) {
        this.label = data[display];
        this.id = data[key];
        this.data = data;
    }
}


function isSelectable(toTest: any): toTest is Selectable {
    return toTest == undefined || ('label' in toTest && 'id' in toTest && 'data' in toTest);
}


@Component({
    selector: 'm4m-selection-list',
    templateUrl: './selection-list.component.html',
    styleUrls: ['./selection-list.component.scss']
})
export class SelectionListComponent implements OnChanges {

    _selectables: Selectable[];

    @Input('selectables') _rawSelectables: any[] = [];

    @Input() display: string = 'id';
    @Input() key: string = 'id';

    @Input() search: string;
    @Input('selected') _selected: any;
    @Output() selectedChange = new EventEmitter();

    highlighted: number = undefined;
    matching: Set<string|number> = new Set<string|number>();

    get selectables(): any[] {
        if (this._selectables != undefined) {
            return this._selectables;
        }
        return [];
    }

    set selectables(selectables: any[]) {
        this._rawSelectables = selectables;
        this.updateSelectables();
    }

    get selected() {
        let selectable: Selectable = undefined;
        let selected = this._selected;
        if (!isSelectable(selected)) {
            if (selected.id === -1) {
                return undefined;
            }
            selected = new Selectable(selected, this.display, this.key);
        }
        if (selected != undefined) {
            for (let sel of this.selectables) {
                if (sel.id === selected.id) {
                    selectable = sel;
                    break;
                }
            }
        }
        return selectable;
    }

    set selected(selected) {
        this._selected = selected;
    }

    ngOnChanges(changes: SimpleChanges): void {
        this.updateSelectables();
        if (changes.search != null) {
            this.updateMatching(this.search);
        }
    }

    updateSelectables() {
        let list = [];
        if (this._rawSelectables != undefined) {
            for (let data of this._rawSelectables) {
                list.push(new Selectable(data, this.display, this.key))
            }
        }
        this._selectables = list.sort((a, b) => ((a.label < b.label) ? -1 : ((a.label > b.label) ? 1 : 0)));
        this.updateMatching(this.search);
    }

    updateMatching(searchString: string) {
        if (this.selectables == undefined || this.display == undefined) {
            return;
        }
        if (searchString == null) {
            searchString = '';
        }
        searchString = searchString.toUpperCase();
        let matches = new Set<string|number>();
        for (let selectable of (this.selectables as Selectable[])) {
            if (selectable.label.toString().toUpperCase().includes(searchString)){
                matches.add(selectable.id);
            }
        }
        if (matches.size > 0) {
            if (this.highlighted == undefined || !matches.has(this.highlighted)) {
                this.highlighted = (matches.values().next().value as any);
            }
        }
        this.matching = matches;
    }

    select(key?: any) {
        if (key == undefined) {
            key = this.highlighted;
        }
        if (key == undefined) {
            return;
        }
        for (let selectable of this.selectables) {
            if (selectable.id === key) {
                this.selectedChange.emit(selectable.data);
            }
        }
        this.updateMatching('')
    }

    highlightSelectable(selectable) {
        if (this.highlighted != selectable.id) {
            this.highlighted = selectable.id;
        }
    }

    highlightNext() {
        let searching = true;
        for (let selectable of (this.selectables as Selectable[])) {
            if (searching && selectable.id === this.highlighted){
                searching = false;
                continue;
            }
            if (!searching && this.matching.has(selectable.id)) {
                this.highlighted = (selectable.id as any);
                return;
            }
        }
    }

    highlightPrevious() {
        let previous: any = this.highlighted;
        for (let selectable of (this.selectables as Selectable[])) {
            if (selectable.id === this.highlighted){
                this.highlighted = previous;
                return;
            }
            if (this.matching.has(selectable.id)) {
                previous = selectable.id;
            }
        }
    }
}

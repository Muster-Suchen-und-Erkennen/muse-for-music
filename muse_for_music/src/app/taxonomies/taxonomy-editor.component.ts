import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, OnInit, OnDestroy } from '@angular/core';

import { ApiObject } from '../shared/rest/api-base.service';
import { ApiService } from '../shared/rest/api.service';
import { Subscription } from 'rxjs/Rx';

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
        if (depth != null) {
            this.depth = depth;
        }
    }
}


@Component({
    selector: 'm4m-taxonomy-editor',
    templateUrl: './taxonomy-editor.component.html',
})
export class TaxonomyEditorComponent implements OnInit, OnDestroy {

    private taxonomyListSubscription: Subscription;
    private taxonomySubscription: Subscription;

    taxonomyList: ApiObject[] = [];

    selectedTaxonomy: string;
    isTree: boolean = false;

    items: TaxonomyItem[];


    closed: Set<number> = new Set<number>();

    openNodes: Set<number> = new Set<number>();


    visible(selectable: TaxonomyItem): boolean {
        if (this.selectedTaxonomy != null && this.isTree) {
            for (const parent of selectable.parents) {
                if (this.closed.has(parent)) {
                    return false;
                }
            }
            return true;
        } else {
            return true;
        }
    }

    constructor(private api: ApiService) {}

    ngOnInit(): void {
        this.taxonomyListSubscription = this.api.getTaxonomies().subscribe((taxonomies: ApiObject) => {
            if (taxonomies == null) {
                this.taxonomyList = [] as ApiObject[];
            }
            this.taxonomyList = taxonomies.taxonomies;
        });
        this.updateTaxonomy();
    }

    ngOnDestroy(): void {
        if (this.taxonomyListSubscription != null) {
            this.taxonomyListSubscription.unsubscribe();
        }
        if (this.taxonomySubscription != null) {
            this.taxonomySubscription.unsubscribe();
        }
    }

    updateTaxonomy(): void {
        if (this.taxonomySubscription != null) {
            this.taxonomySubscription.unsubscribe();
        }
        if (this.selectedTaxonomy == null) {
            return;
        }
        this.taxonomySubscription = this.api.getTaxonomy(this.selectedTaxonomy).subscribe(taxonomy => {
            if (taxonomy == null) {
                return;
            }
            if (taxonomy.taxonomy_type === 'tree') {
                this.isTree = true;
                this.prepareTreeTaxonomy(taxonomy.items);
            } else {
                this.isTree = false;
                this.prepareListTaxonomy(taxonomy.items);
            }
            this.closed.clear();
        });
    }

    prepareListTaxonomy(items) {
        const temp = [];
        for (const item of items) {
            temp.push(new TaxonomyItem(item));
        }
        this.items = temp;
    }

    prepareTreeTaxonomy(item, flatList?: TaxonomyItem[], parents?: Set<TaxonomyItem>) {
        let recursionStart = false;
        if (parents == null) {
            parents = new Set<TaxonomyItem>();
        }
        if (flatList == null) {
            flatList = [];
            recursionStart = true;
        }
        const children = item.children;

        const node = new TaxonomyItem(item, parents.size);
        flatList.push(node);

        parents.forEach(parent => {
            parent.children.push(node.id);
            node.parents.push(parent.id);
        });

        parents.add(node);
        for (const child of children) {
            this.prepareTreeTaxonomy(child, flatList, parents);
        }
        parents.delete(node);

        if (recursionStart) {
            this.items = flatList;
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
    }
}
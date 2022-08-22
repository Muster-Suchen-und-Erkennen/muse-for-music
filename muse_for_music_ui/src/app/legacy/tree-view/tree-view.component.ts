import { TreeService } from './../tree/tree.service';
import { TREE } from './../tree/mock-tree';
import { Component, OnInit } from '@angular/core';



@Component({
  selector: 'm4m-tree-view',
  templateUrl: './tree-view.component.html',
  styleUrls: ['./tree-view.component.scss']
})
export class TreeViewComponent implements OnInit {

  nodes: TREE[];

  constructor(private treeService: TreeService) { }

  getTree(): void {
    this.nodes = this.treeService.getTree();
  }

  ngOnInit(): void {
    this.getTree();
  }

}

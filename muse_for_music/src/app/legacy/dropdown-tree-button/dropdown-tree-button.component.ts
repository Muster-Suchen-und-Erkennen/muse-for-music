import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'm4m-dropdown-tree-button',
  templateUrl: './dropdown-tree-button.component.html',
  styleUrls: ['./dropdown-tree-button.component.scss']
})
export class DropdownTreeButtonComponent implements OnInit {

  public status: {isopen: boolean} = {isopen: false};

  public toggleDropdown($event: MouseEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.status.isopen = !this.status.isopen;

  }

  constructor() { }

  ngOnInit() {
  }

}

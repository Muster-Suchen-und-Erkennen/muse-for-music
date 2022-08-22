import { Component } from '@angular/core';

@Component({
    selector: 'm4m-dropdown',
    templateUrl: './dropdown.component.html',
    styleUrls: ['./dropdown.component.scss']
})
export class myDropdownComponent {
    open: boolean = false;

    public openDropdown() {
        this.open = true;
    }

    public closeDropdown() {
        this.open = false;
    }

    public toggleDropdown() {
        this.open = ! this.open;
    }
}

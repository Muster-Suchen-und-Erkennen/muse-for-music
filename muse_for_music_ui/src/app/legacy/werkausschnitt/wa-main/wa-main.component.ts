import { Router, PRIMARY_OUTLET } from '@angular/router';
import { PARTS, Part } from './../werkausschnitt-parts';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'm4m-wa-main',
  templateUrl: './wa-main.component.html',
  styleUrls: ['./wa-main.component.scss']
})
export class WaMainComponent implements OnInit {
  parts: Part[] = PARTS;
  selectedId: number = -1;

  constructor(private router: Router) {
  }

  ngOnInit() {
  }

  onSelect(id: number): void {
    this.selectedId = id;
  }

  mod(n: number, m: number): number {
    return ((n % m) + m) % m;
  }

  extractChildUrl(): string {
    return this.router.parseUrl(this.router.url).root.children[PRIMARY_OUTLET].segments[1].toString();

  }

  selectNext(): void {
    const currentPath: string = this.extractChildUrl();
    let nextId: number;
    for (const id in this.parts) {
      if (this.parts[id].path === currentPath) {
        nextId = this.mod((parseInt(id, 10) + 1), this.parts.length);
        break;
      }
    }
    this.router.navigate(['werkausschnitt/' + this.parts[nextId].path]);
  }

  selectPrevious(): void {
    const currentPath: string = this.extractChildUrl();
    let nextId: number;
    for (const id in this.parts) {
      if (this.parts[id].path === currentPath) {
        nextId = this.mod((parseInt(id, 10) - 1), this.parts.length);
        break;
      }
    }
    console.log(nextId);
    this.router.navigate(['werkausschnitt/' + this.parts[nextId].path]);
  }
}

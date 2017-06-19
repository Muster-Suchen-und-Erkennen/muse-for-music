import { DummyComponent } from './werkausschnitt/dummy/dummy.component';
import { DropdownTreeButtonComponent } from './dropdown-tree-button/dropdown-tree-button.component';

import { AppComponent } from './app.component';
import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

const routes: Routes = [
  { path: 'werkausschnitt', loadChildren: 'app/werkausschnitt/werkausschnitt.module#WerkausschnittModule' },
  { path: 'treeselect', component: DropdownTreeButtonComponent },
  { path: '', pathMatch: 'full', redirectTo: 'treeselect'},
  { path: '**', redirectTo: '' }
]

@NgModule({
  imports: [
    RouterModule.forRoot(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule { }

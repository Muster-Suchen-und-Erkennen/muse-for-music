import { DummyComponent } from './legacy/werkausschnitt/dummy/dummy.component';
import { DropdownTreeButtonComponent } from './legacy/dropdown-tree-button/dropdown-tree-button.component';

import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { HomeComponent } from './home/home.component';
import { PeopleOverviewComponent } from './people/people-overview.component';

const routes: Routes = [
  { path: 'werkausschnitt', loadChildren: 'app/werkausschnitt/werkausschnitt.module#WerkausschnittModule' },
  { path: 'treeselect', component: DropdownTreeButtonComponent },

  { path: 'people', component: PeopleOverviewComponent },
  { path: '', pathMatch: 'full', component: HomeComponent},
  { path: '**', redirectTo: 'dashboard' }
]

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {useHash: true})
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule { }

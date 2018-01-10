import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { HomeComponent } from './home/home.component';
import { PeopleOverviewComponent } from './people/people-overview.component';
import { OpusesOverviewComponent } from './opuses/opuses-overview.component';
import { OpusEditComponent } from './opuses/opus-edit.component';

const routes: Routes = [
  { path: 'people', component: PeopleOverviewComponent },
  { path: 'opuses', component: OpusesOverviewComponent},
  { path: 'opuses/:id', component: OpusEditComponent},
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

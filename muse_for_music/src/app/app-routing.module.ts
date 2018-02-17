import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { HomeComponent } from './home/home.component';
import { PeopleOverviewComponent } from './people/people-overview.component';
import { OpusesOverviewComponent } from './opuses/opuses-overview.component';
import { OpusDetailComponent } from './opuses/opus-detail.component';

const routes: Routes = [
  { path: 'people', component: PeopleOverviewComponent },
  { path: 'opuses', component: OpusesOverviewComponent},
  { path: 'opuses/:id', component: OpusDetailComponent},
  { path: 'parts/:id', redirectTo: ''},
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

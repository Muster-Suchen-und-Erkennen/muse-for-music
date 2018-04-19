import { Routes, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { UserManagementComponent } from './users/user-management.component';
import { UserOverviewComponent } from './users/user-overview.component';

import { PeopleOverviewComponent } from './people/people-overview.component';
import { OpusesOverviewComponent } from './opuses/opuses-overview.component';
import { OpusDetailComponent } from './opuses/opus-detail.component';
import { PartDetailComponent } from './parts/part-detail.component';
import { SubPartDetailComponent } from './subparts/subpart-detail.component';
import { VoiceDetailComponent } from './voices/voice-detail.component';

import { LoginGuard } from './shared/rest/login.guard';
import { AdminGuard } from './shared/rest/admin.guard';

const routes: Routes = [
  { path: 'people', component: PeopleOverviewComponent, canActivate: [LoginGuard] },
  { path: 'opuses', component: OpusesOverviewComponent, canActivate: [LoginGuard] },
  { path: 'opuses/:id', component: OpusDetailComponent, canActivate: [LoginGuard] },
  { path: 'parts/:id', component: PartDetailComponent, canActivate: [LoginGuard] },
  { path: 'subparts/:id', component: SubPartDetailComponent, canActivate: [LoginGuard] },
  { path: 'subparts/:subpartID/voices/:voiceID', component: VoiceDetailComponent, canActivate: [LoginGuard] },
  { path: '', pathMatch: 'full', component: HomeComponent, canActivate: [LoginGuard] },
  { path: 'login', pathMatch: 'full', component: LoginComponent},
  { path: 'user', pathMatch: 'full', component: UserOverviewComponent, canActivate: [LoginGuard]},
  { path: 'users', pathMatch: 'full', component: UserManagementComponent, canActivate: [AdminGuard]},
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

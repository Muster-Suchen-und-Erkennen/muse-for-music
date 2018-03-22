import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpModule} from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';


import { WerkausschnittModule } from './legacy/werkausschnitt/werkausschnitt.module';
import { TreeModule } from 'angular-tree-component';
import { DropdownTreeButtonComponent } from './legacy/dropdown-tree-button/dropdown-tree-button.component';
import { BsDropdownModule } from 'ngx-bootstrap/dropdown';
import { TreeService } from './legacy/tree/tree.service';
import { TreeViewComponent } from './legacy/tree-view/tree-view.component';


import {SharedModule} from './shared/shared.module';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';

import { HomeComponent } from './home/home.component';
import { PeopleOverviewComponent } from './people/people-overview.component';
import { PersonEditComponent } from './people/person-edit.component';
import { OpusesOverviewComponent } from './opuses/opuses-overview.component';
import { OpusDetailComponent } from './opuses/opus-detail.component';
import { OpusEditComponent } from './opuses/opus-edit.component';
import { OpusPartsComponent } from './opuses/opus-parts.component';
import { PartDetailComponent } from './parts/part-detail.component';
import { PartEditComponent } from './parts/part-edit.component';
import { PartSubpartsComponent } from './parts/part-subparts.component';

import { AppComponent } from './app.component';


@NgModule({
  declarations: [
    AppComponent,

    HomeComponent,
    PeopleOverviewComponent,
    PersonEditComponent,
    OpusesOverviewComponent,
    OpusDetailComponent,
    OpusEditComponent,
    OpusPartsComponent,
    PartDetailComponent,
    PartEditComponent,
    PartSubpartsComponent,

    BreadcrumbsComponent,
    TitleBarComponent,
  ],
  imports: [
    HttpModule,
    BrowserModule,
    ReactiveFormsModule,
    TreeModule,
    SharedModule,
    BsDropdownModule.forRoot(),
    AppRoutingModule
  ],
  providers: [TreeService,
    NavigationService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

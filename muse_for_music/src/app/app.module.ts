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

import { BaseApiService } from './rest/api-base.service';
import { ApiService } from './rest/api.service';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';

import { HomeComponent } from './home/home.component';
import { PeopleOverviewComponent } from './people/people-overview.component';
import { PersonEditComponent } from './people/person-edit.component';

import { AppComponent } from './app.component';


@NgModule({
  declarations: [
    AppComponent,
    DropdownTreeButtonComponent,
    TreeViewComponent,

    HomeComponent,
    PeopleOverviewComponent,
    PersonEditComponent,
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
    BaseApiService,
    ApiService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

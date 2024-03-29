import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { registerLocaleData } from '@angular/common';
import de from '@angular/common/locales/de';
import localeDeExtra from '@angular/common/locales/extra/de';


import {SharedModule} from './shared/shared.module';

import { BreadcrumbsComponent } from './navigation/breadcrumbs.component';
import { TitleBarComponent } from './navigation/title-bar.component';
import { NavigationService } from './navigation/navigation-service';

import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';

import { UserManagementComponent } from './users/user-management.component';
import { UserOverviewComponent } from './users/user-overview.component';
import { UserDetailComponent } from './users/user-detail.component';

import { TaxonomyEditorComponent } from './taxonomies/taxonomy-editor.component';
import { HistoryComponent } from './history/history.component';

import { PeopleOverviewComponent } from './people/people-overview.component';
import { PersonEditComponent } from './people/person-edit.component';
import { OpusesOverviewComponent } from './opuses/opuses-overview.component';
import { OpusDetailComponent } from './opuses/opus-detail.component';
import { OpusEditComponent } from './opuses/opus-edit.component';
import { OpusPartsComponent } from './opuses/opus-parts.component';
import { PartDetailComponent } from './parts/part-detail.component';
import { PartEditComponent } from './parts/part-edit.component';
import { PartSubpartsComponent } from './parts/part-subparts.component';
import { SubPartDetailComponent } from './subparts/subpart-detail.component';
import { SubPartEditComponent } from './subparts/subpart-edit.component';
import { SubPartVoicesComponent } from './subparts/subpart-voices.component';
import { VoiceDetailComponent } from './voices/voice-detail.component';
import { VoiceEditComponent } from './voices/voice-edit.component';

import { AppComponent } from './app.component';

// register locales
registerLocaleData(de, 'de-DE', localeDeExtra);


@NgModule({
  declarations: [
    AppComponent,

    LoginComponent,
    HomeComponent,

    UserManagementComponent,
    UserOverviewComponent,
    UserDetailComponent,

    TaxonomyEditorComponent,
    HistoryComponent,

    PeopleOverviewComponent,
    PersonEditComponent,
    OpusesOverviewComponent,
    OpusDetailComponent,
    OpusEditComponent,
    OpusPartsComponent,
    PartDetailComponent,
    PartEditComponent,
    PartSubpartsComponent,
    SubPartDetailComponent,
    SubPartEditComponent,
    SubPartVoicesComponent,
    VoiceDetailComponent,
    VoiceEditComponent,

    BreadcrumbsComponent,
    TitleBarComponent,
  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    ReactiveFormsModule,
    SharedModule,
    AppRoutingModule
  ],
  providers: [
    NavigationService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

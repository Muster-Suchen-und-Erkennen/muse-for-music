import { WerkausschnittModule } from './werkausschnitt/werkausschnitt.module';
import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { TreeModule } from 'angular-tree-component';
import { AppComponent } from './app.component';
import { DropdownTreeButtonComponent } from './dropdown-tree-button/dropdown-tree-button.component';
import { BsDropdownModule } from 'ngx-bootstrap/dropdown';
import { TreeService } from './tree/tree.service';
import { TreeViewComponent } from './tree-view/tree-view.component';


@NgModule({
  declarations: [
    AppComponent,
    DropdownTreeButtonComponent,
    TreeViewComponent,
  ],
  imports: [
    BrowserModule,
    TreeModule,
    BsDropdownModule.forRoot(),
    AppRoutingModule
  ],
  providers: [TreeService],
  bootstrap: [AppComponent]
})
export class AppModule { }

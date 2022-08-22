import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WerkausschnittRoutingModule } from './werkausschnitt-routing.module';
import { WaMainComponent } from './wa-main/wa-main.component';
import { DummyComponent } from './dummy/dummy.component';
import { WaSatzComponent } from './wa-satz/wa-satz.component';

@NgModule({
  imports: [
    CommonModule,
    WerkausschnittRoutingModule
  ],
  exports: [
    WaMainComponent
  ],
  declarations: [WaMainComponent, DummyComponent, WaSatzComponent]
})
export class WerkausschnittModule { }

import { PARTS } from './werkausschnitt-parts';
import { WaMainComponent } from './wa-main/wa-main.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DummyComponent } from './dummy/dummy.component';

const routesOfParts: Routes = [];

for (const part of PARTS) {
  routesOfParts.push({path: part.path, component: part.component})
}
routesOfParts.push({ path: '', component: DummyComponent} )

const routes: Routes = [
  { path: '', component: WaMainComponent, children: routesOfParts}
];
@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class WerkausschnittRoutingModule { }

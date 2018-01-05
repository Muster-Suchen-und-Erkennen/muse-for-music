import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { myBoxComponent } from './box/box.component';

@NgModule({
    imports:      [ CommonModule ],
    declarations: [ myBoxComponent ],
    exports: [
        myBoxComponent, CommonModule
    ]
})
export class SharedModule { }

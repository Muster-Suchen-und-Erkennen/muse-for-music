import { WaSatzComponent } from './wa-satz/wa-satz.component';
import { DummyComponent } from './dummy/dummy.component';
export class Part {
    id: number;
    text: string;
    path: string;
    component: any;
}

export const PARTS: Part[] = [
    { id: 0, text: 'Satz', path: 'satz', component: WaSatzComponent },
    { id: 1, text: 'Rhythmik', path: 'rhythmik', component: DummyComponent },
    { id: 2, text: 'Weiteres', path: 'weiteres', component: DummyComponent },
    { id: 3, text: 'Noch mehr', path: 'noch-mehr', component: DummyComponent },
]

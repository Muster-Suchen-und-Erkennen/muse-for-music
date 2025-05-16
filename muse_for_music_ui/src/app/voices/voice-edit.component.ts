import { Component, OnChanges, Input, ViewChild, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { DynamicFormComponent } from '../shared/forms/dynamic-form/dynamic-form.component';
import { take } from 'rxjs/operators';
import { Subscription } from 'rxjs';

@Component({
  selector: 'm4m-voice-edit',
  templateUrl: './voice-edit.component.html',
  styleUrls: ['./voice-edit.component.scss']
})
export class VoiceEditComponent implements OnChanges, OnDestroy {

    @Input() subPartID: number;
    @Input() voiceID: number;

    @ViewChild(DynamicFormComponent) form;

    voice: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    subpart: ApiObject;

    private subPartSub: Subscription|null = null;
    private voiceSub: Subscription|null = null;

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        if (this.subPartSub != null) {
            this.subPartSub.unsubscribe();
        }
        this.subPartSub = this.api.getSubPart(this.subPartID).subscribe(subpart => {
            if (subpart == undefined) {
                return;
            }
            this.subpart = subpart;
            if (this.voiceSub != null) {
                this.voiceSub.unsubscribe();
            }
            this.voiceSub = this.api.getVoice(subpart, this.voiceID).subscribe(voice => {
                this.voice = voice;
            });
        });
    }

    ngOnDestroy(): void {
        if (this.subPartSub != null) {
            this.subPartSub.unsubscribe();
        }
        if (this.voiceSub != null) {
            this.voiceSub.unsubscribe();
        }
    }

    save(event) {
        this.api.putVoice(this.subpart, this.voice.id, event).pipe(take(1)).subscribe(() => {
            this.form.saveFinished(true);
        }, () => {
            this.form.saveFinished(false);
        });
    }

    delete = () => {
        this.api.deleteVoice(this.subpart, this.voice).pipe(take(1)).subscribe(() => this.router.navigate(['subparts', this.subpart.id]));
    };

}

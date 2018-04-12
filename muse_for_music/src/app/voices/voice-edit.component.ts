import { Component, OnChanges, Input } from '@angular/core';
import { Router } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';

@Component({
  selector: 'm4m-voice-edit',
  templateUrl: './voice-edit.component.html',
  styleUrls: ['./voice-edit.component.scss']
})
export class VoiceEditComponent implements OnChanges {

    @Input() subPartID: number;
    @Input() voiceID: number;

    voice: ApiObject = {
        _links: {'self': {'href': ''}},
        name: 'UNBEKANNT'
    };

    private subpart: ApiObject;

    valid: boolean = false;
    data: any = {};

    constructor(private api: ApiService, private router: Router) { }

    ngOnChanges(): void {
        this.api.getSubPart(this.subPartID).subscribe(subpart => {
            if (subpart == undefined) {
                return;
            }
            this.subpart = subpart;
            this.api.getVoice(subpart, this.voiceID).subscribe(voice => {
                this.voice = voice;
            })
        });
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.data = data;
    }

    save(event) {
        if (this.valid) {
            this.api.putVoice(this.subpart, this.voice.id, this.data);
        }
    }

    delete = () => {
        this.api.deleteVoice(this.subpart, this.voice).take(1).subscribe(() => this.router.navigate(['subparts', this.subpart.id]));
    };

}

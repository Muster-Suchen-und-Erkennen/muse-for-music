import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { NavigationService, Breadcrumb } from '../navigation/navigation-service';
import { Subscription } from 'rxjs';
import { UserApiService } from 'app/shared/rest/user-api.service';

@Component({
  selector: 'm4m-voice-detail',
  templateUrl: './voice-detail.component.html',
  styleUrls: ['./voice-detail.component.scss']
})
export class VoiceDetailComponent implements OnInit, OnDestroy {

    private paramSubscription: Subscription;
    private subPartSubscription: Subscription;
    private voiceSubscription: Subscription;
    private partSubscription: Subscription;
    private opusSubscription: Subscription;

    subPartID: number;
    voiceID: number;
    voice: ApiObject;

    constructor(private navigation: NavigationService, private api: ApiService, private userApi: UserApiService, private route: ActivatedRoute) { }

    update(subPartID: number, voiceID: number) {
        this.subPartID = subPartID;
        this.voiceID = voiceID;
        this.navigation.changeTitle('Voice');
        this.navigation.changeBreadcrumbs([new Breadcrumb('Teilwerkausschnitte', '/subparts'),
            new Breadcrumb('"' + subPartID.toString() + '"', '/subparts/' + subPartID),
            new Breadcrumb('Stimmen', '/voices'),
            new Breadcrumb('"' + voiceID.toString() + '"', '/subparts/' + subPartID + '/voices/' + voiceID)]);

        if (this.subPartSubscription != null) {
            this.subPartSubscription.unsubscribe();
        }
        this.subPartSubscription = this.api.getSubPart(subPartID).subscribe(subpart => {
            if (subpart == undefined) {
                return;
            }

            this.navigation.changeBreadcrumbs([new Breadcrumb('Werkausschnitte', '/parts'),
                new Breadcrumb('"' + subpart.part_id.toString() + '"', '/parts/' + subpart.part_id),
                new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID),
                new Breadcrumb('Stimmen', '/voices'),
                new Breadcrumb('"' + voiceID.toString() + '"', '/subparts/' + subPartID + '/voices/' + voiceID)]);


            if (this.voiceSubscription != null) {
                this.voiceSubscription.unsubscribe();
            }
            this.voiceSubscription = this.api.getVoice(subpart, voiceID).subscribe(voice => {
                if (voice == undefined) {
                    return;
                }
                this.voice = voice;

                this.navigation.changeBreadcrumbs([new Breadcrumb('Werkausschnitte', '/parts'),
                    new Breadcrumb('"' + subpart.part_id.toString() + '"', '/parts/' + subpart.part_id),
                    new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                    new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID),
                    new Breadcrumb('Stimmen', '/voices'),
                    new Breadcrumb('"' + voice.name + '"', '/subparts/' + subPartID + '/voices/' + voiceID)]);

                if (this.partSubscription != null) {
                    this.partSubscription.unsubscribe();
                }
                this.partSubscription = this.api.getPart(subpart.part_id).subscribe(part => {
                    if (part == undefined) {
                        return;
                    }
                    this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
                        new Breadcrumb('"' + part.opus_id.toString() + '"', '/opuses/' + part.opus_id),
                        new Breadcrumb('Werkausschnitte', '/parts'),
                        new Breadcrumb('"' + part.name + '"', '/parts/' + part.id),
                        new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                        new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID),
                        new Breadcrumb('Stimmen', '/voices'),
                        new Breadcrumb('"' + voice.name + '"', '/subparts/' + subPartID + '/voices/' + voiceID)]);

                    if (this.opusSubscription != null) {
                        this.opusSubscription.unsubscribe();
                    }
                    this.opusSubscription = this.api.getOpus(part.opus_id).subscribe(opus => {
                        if (opus == undefined) {
                            return;
                        }
                        this.navigation.changeBreadcrumbs([new Breadcrumb('Werke', '/opuses'),
                            new Breadcrumb('"' + opus.name + '"', '/opuses/' + part.opus_id),
                            new Breadcrumb('Werkausschnitte', '/parts'),
                            new Breadcrumb('"' + part.name + '"', '/parts/' + part.id),
                            new Breadcrumb('Teilwerkausschnitte', '/subparts'),
                            new Breadcrumb('"' + subpart.label + '"', '/subparts/' + subPartID),
                            new Breadcrumb('Stimmen', '/voices'),
                            new Breadcrumb('"' + voice.name + '"', '/subparts/' + subPartID + '/voices/' + voiceID)]);
                    });
                });
            });
        });
    }

    ngOnInit(): void {
        this.navigation.changeTitle('Stimme');
        this.paramSubscription = this.route.params.subscribe(params => {
            this.update(parseInt(params['subpartID'], 10), parseInt(params['voiceID'], 10));
        });
    }

    ngOnDestroy(): void {
        if (this.paramSubscription != null) {
            this.paramSubscription.unsubscribe();
        }
        if (this.opusSubscription != null) {
            this.opusSubscription.unsubscribe();
        }
        if (this.partSubscription != null) {
            this.partSubscription.unsubscribe();
        }
        if (this.subPartSubscription != null) {
            this.subPartSubscription.unsubscribe();
        }
        if (this.voiceSubscription != null) {
            this.voiceSubscription.unsubscribe();
        }
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }
}

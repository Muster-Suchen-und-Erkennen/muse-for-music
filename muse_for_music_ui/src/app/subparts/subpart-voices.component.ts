import { Component, OnInit, Input, Testability } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';
import { TableRow } from '../shared/table/table.component';
import { UserApiService } from 'app/shared/rest/user-api.service';

@Component({
  selector: 'm4m-subpart-voices',
  templateUrl: './subpart-voices.component.html',
  styleUrls: ['./subpart-voices.component.scss']
})
export class SubPartVoicesComponent implements OnInit {

    @Input() subPartID: number;

    subpart: ApiObject;
    voices: Array<ApiObject>;
    tableData: TableRow[];

    swagger: any;

    valid: boolean;

    newVoiceData: any;

    constructor(private api: ApiService, private userApi: UserApiService) { }

    ngOnInit(): void {
        this.api.getSubPart(this.subPartID).subscribe(data => {
            if (data == undefined) {
                return;
            }
            this.subpart = data;
            this.voices = this.subpart.voices;
            this.api.getVoices(data).subscribe(data => {
                if (data == undefined) {
                    return;
                }
                this.voices = data;
                const tableData = [];
                this.voices.forEach(voice => {
                    const row = new TableRow(voice.id, [voice.name, voice.measure_start.measure, voice.measure_end.measure],
                                             ['subparts', this.subPartID, 'voices', voice.id]);
                    tableData.push(row);
                });
                this.tableData = tableData;
            });
        });
    }

    showEditButton() {
        return this.userApi.loggedIn && this.userApi.roles.has('user') && this.userApi.isEditing();
    }


    save = () => {
        if (this.valid) {
            this.api.postVoice(this.subpart, this.newVoiceData).subscribe(_ => {return});
        }
    };

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newVoiceData = data;
    }
}

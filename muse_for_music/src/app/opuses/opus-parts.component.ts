import { Component, OnInit, Input } from '@angular/core';
import { ApiService } from '../shared/rest/api.service';
import { ApiObject } from '../shared/rest/api-base.service';

@Component({
  selector: 'm4m-opus-parts',
  templateUrl: './opus-parts.component.html',
  styleUrls: ['./opus-parts.component.scss']
})
export class OpusPartsComponent implements OnInit {

    @Input opusID: number;

    opus: ApiObject;
    parts: Array<ApiObject>;

    swagger: any;

    valid: boolean;

    newPartData: any;

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.api.getOpus(this.opusID).subscribe(data => {
            this.opus = data;
            this.parts = this.opus.parts;
            this.api.getParts(data).subscribe(data => this.parts = data);
        });
    }

    newPart(event) {
        if (this.valid) {
            //this.api.postPart(this.newPartData).subscribe(_ => {return});
        }
    }

    onValidChange(valid: boolean) {
        this.valid = valid;
    }

    onDataChange(data: any) {
        this.newPartData = data;
    }
}

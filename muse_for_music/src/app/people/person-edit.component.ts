import { Component, OnInit, Input } from '@angular/core';
import { FormControl, FormGroup }            from '@angular/forms';
import { ApiService } from '../rest/api.service';
import { ApiObject } from '../rest/api-base.service';

@Component({
  selector: 'm4m-person-edit',
  templateUrl: './person-edit.component.html',
  styleUrls: ['./person-edit.component.scss']
})
export class PersonEditComponent implements OnInit {

    @Input() personID: number;
    person: ApiObject = {
        _links: {'self':{'href':''}},
        name: 'UNBEKANNT'
    };

    personForm = new FormGroup ({
        name: new FormControl(),
        birht_date: new FormControl(),
    });

    constructor(private api: ApiService) { }

    ngOnInit(): void {
        this.api.getPerson(this.personID).subscribe(data => {
            this.person = data;
            this.personForm.patchValue(data);
        });
    }

}
import { Component } from '@angular/core';

import { UserApiService } from '../shared/rest/user-api.service';

@Component({
  selector: 'm4m-user-detail',
  templateUrl: './user-detail.component.html',
})
export class UserDetailComponent {


    constructor(private userApi: UserApiService) { }
}

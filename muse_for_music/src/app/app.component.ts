import { Component, ViewChild } from '@angular/core';
import { UserApiService } from './shared/rest/user-api.service';
import { myDialogComponent } from './shared/dialog/dialog.component';

@Component({
    selector: 'm4m-root',
    templateUrl: './app.component.html'
})
export class AppComponent {
    title = 'app';

    @ViewChild('renewLoginDialog') loginDialog: myDialogComponent;
    private password: string;


    constructor(private userApi: UserApiService) {
        userApi.sessionExpiry.subscribe(() => {
            this.loginDialog.open();
        });
    }

    renewLogin = () => {
        if (!this.userApi.tokenIsFresh) {
            this.userApi.freshLogin(this.password);
        }
    }
}

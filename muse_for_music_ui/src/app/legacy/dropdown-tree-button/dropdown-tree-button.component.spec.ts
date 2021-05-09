import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { DropdownTreeButtonComponent } from './dropdown-tree-button.component';

describe('DropdownTreeButtonComponent', () => {
  let component: DropdownTreeButtonComponent;
  let fixture: ComponentFixture<DropdownTreeButtonComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ DropdownTreeButtonComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DropdownTreeButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

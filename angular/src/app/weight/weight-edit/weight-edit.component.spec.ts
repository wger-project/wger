import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeightEditComponent } from './weight-edit.component';

describe('WeightEditComponent', () => {
  let component: WeightEditComponent;
  let fixture: ComponentFixture<WeightEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightEditComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WeightEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

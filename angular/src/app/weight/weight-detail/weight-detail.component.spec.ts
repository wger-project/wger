import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeightDetailComponent } from './weight-detail.component';

describe('WightDetailComponent', () => {
  let component: WeightDetailComponent;
  let fixture: ComponentFixture<WeightDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightDetailComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WeightDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {weightEntry1} from '../test-data/weight';
import {WeightService} from '../weight.service';

import { WeightDetailComponent } from './weight-detail.component';

describe('WeightDetailComponent', () => {
  let component: WeightDetailComponent;
  let fixture: ComponentFixture<WeightDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightDetailComponent ],
      imports: [HttpClientTestingModule],
      providers: [WeightService]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WeightDetailComponent);
    component = fixture.componentInstance;

    component.entry = weightEntry1;
    component.weightDiff = -1;
    component.dayDiff = 2;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

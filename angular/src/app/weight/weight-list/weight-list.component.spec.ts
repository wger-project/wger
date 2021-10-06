import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {WeightService} from '../weight.service';

import { WeightListComponent } from './weight-list.component';

describe('ExerciseListComponent', () => {
  let component: WeightListComponent;
  let fixture: ComponentFixture<WeightListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightListComponent ],
      providers: [WeightService],
      imports: [HttpClientTestingModule]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WeightListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

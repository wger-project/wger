import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {FormBuilder} from '@angular/forms';
import {WeightService} from '../weight.service';

import { WeightEditComponent } from './weight-edit.component';

describe('WeightEditComponent', () => {
  let component: WeightEditComponent;
  let fixture: ComponentFixture<WeightEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightEditComponent ],
      providers: [WeightService, FormBuilder],
      imports: [HttpClientTestingModule]
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

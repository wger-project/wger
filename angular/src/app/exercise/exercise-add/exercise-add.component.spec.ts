import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {RouterTestingModule} from '@angular/router/testing';
import {ExerciseService} from '../exercise.service';

import { ExerciseAddComponent } from './exercise-add.component';

describe('ExerciseAddComponent', () => {
  let component: ExerciseAddComponent;
  let fixture: ComponentFixture<ExerciseAddComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExerciseAddComponent ],
      imports: [HttpClientTestingModule, RouterTestingModule],
      providers: [ExerciseService]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExerciseAddComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

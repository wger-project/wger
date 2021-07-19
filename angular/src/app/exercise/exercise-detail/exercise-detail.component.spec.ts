import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {ExerciseService} from '../exercise.service';
import {Category} from '../models/exercises/category.model';
import {Exercise} from '../models/exercises/exercise.model';

import {ExerciseDetailComponent} from './exercise-detail.component';

describe('ExerciseComponent', () => {
  let component: ExerciseDetailComponent;
  let fixture: ComponentFixture<ExerciseDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ExerciseDetailComponent],
      imports: [HttpClientTestingModule],
      providers: [ExerciseService]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExerciseDetailComponent);
    component = fixture.componentInstance;
    component.exercise = new Exercise(1,
      'abcd',
      'Cool exercise',
      new Date(2021, 5, 10),
      'Take the weight, move it. ',
      1,
      [1, 2, 3],
      [5, 6],
      [1, 8],
      2,
      'author',
      [2]);
    component.exercise.category = new Category(1, 'Arms');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {ExerciseDetailComponent} from '../exercise-detail/exercise-detail.component';
import {ExerciseService} from '../exercise.service';
import {exercise1} from '../test-data/exercise';

import { ExercisePreviewComponent } from './exercise-preview.component';

describe('ExercisePreviewComponent', () => {
  let component: ExercisePreviewComponent;
  let fixture: ComponentFixture<ExercisePreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ExercisePreviewComponent],
      imports: [HttpClientTestingModule],
      providers: [ExerciseService]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExercisePreviewComponent);
    component = fixture.componentInstance;
    component.exercise = exercise1;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

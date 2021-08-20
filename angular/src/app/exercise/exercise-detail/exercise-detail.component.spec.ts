import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {ActivatedRoute} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {ExerciseService} from '../exercise.service';
import {exercise1} from '../test-data/exercise';

import {ExerciseDetailComponent} from './exercise-detail.component';

describe('ExerciseDetailComponent', () => {
  let component: ExerciseDetailComponent;
  let fixture: ComponentFixture<ExerciseDetailComponent>;

  const fakeActivatedRoute = {
    snapshot: {
      queryParamMap: {
        get(): number {
          return 6;
        }
      }
    }
  };


  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ExerciseDetailComponent],
      imports: [HttpClientTestingModule, RouterTestingModule],
      providers: [ExerciseService, {provide: ActivatedRoute, useValue: fakeActivatedRoute}]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExerciseDetailComponent);
    component = fixture.componentInstance;
    component.exercise = exercise1;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

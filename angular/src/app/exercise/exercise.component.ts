import {Component, OnInit} from '@angular/core';
import {ExerciseService} from './exercise.service';
import {Exercise} from './models/exercise.model';

@Component({
  selector: 'app-exercise',
  templateUrl: './exercise.component.html',
  styleUrls: ['./exercise.component.css']
})
export class ExerciseComponent implements OnInit {

  exercises: Exercise[] = [];

  constructor(private exerciseService: ExerciseService) {

  }

  ngOnInit(): void {
    this.getExercises();
  }

  getExercises(): void {

    this.exerciseService.getExercises().subscribe({
      next: value => {
        this.exercises = value.results;
        // console.log(value.results);
      }
    });
  }

}

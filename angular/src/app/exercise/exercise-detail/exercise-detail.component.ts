import {Component, Input} from '@angular/core';
import {Exercise} from '../models/exercises/exercise.model';

@Component({
  selector: 'app-exercise-detail',
  templateUrl: './exercise-detail.component.html',
  styleUrls: ['./exercise-detail.component.css']
})
export class ExerciseDetailComponent {

  @Input() exercise!: Exercise;

  constructor() {
  }
}

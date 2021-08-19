import {Component, Input, OnInit} from '@angular/core';
import {Exercise} from '../models/exercise.model';

@Component({
  selector: 'app-exercise-preview',
  templateUrl: './exercise-preview.component.html',
  styleUrls: ['./exercise-preview.component.css']
})
export class ExercisePreviewComponent {

  @Input() exercise!: Exercise;

  constructor() { }

}

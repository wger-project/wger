import {Component, Input, OnInit} from '@angular/core';
import {Exercise} from '../models/exercise.model';

@Component({
  selector: 'app-exercise-detail',
  templateUrl: './exercise-detail.component.html',
  styleUrls: ['./exercise-detail.component.css']
})
export class ExerciseDetailComponent implements OnInit {

  @Input() exercise!: Exercise;

  constructor() {
  }

  ngOnInit(): void {
  }


}

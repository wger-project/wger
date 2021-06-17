import { Component, OnInit } from '@angular/core';
import {ExerciseService} from '../exercise.service';
import {Exercise} from '../models/exercise.model';

@Component({
  selector: 'app-exercise-list',
  templateUrl: './exercise-list.component.html',
  styleUrls: ['./exercise-list.component.css']
})
export class ExerciseListComponent implements OnInit {
  exercises: Exercise[] = [];

  constructor(private exerciseService: ExerciseService) { }

  ngOnInit(): void {
    this.getExercises();
  }

  async getExercises(): Promise<void> {
    this.exercises = await this.exerciseService.loadExercises();
  }

  async loadExercise(id: number): Promise<void> {

    const tmp = await this.exerciseService.getExercise(id);
    //console.log(tmp);
  }
}

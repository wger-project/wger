import { Component, OnInit } from '@angular/core';
import {ExerciseService} from '../exercise.service';
import {Category} from '../models/category.model';
import {Equipment} from '../models/equipment.model';
import {Exercise} from '../models/exercise.model';
import {Muscle} from '../models/muscle.model';

@Component({
  selector: 'app-exercise-add',
  templateUrl: './exercise-add.component.html',
  styleUrls: ['./exercise-add.component.css']
})
export class ExerciseAddComponent implements OnInit {

  exercises: Exercise[] = [];
  categories: Category[] = [];
  muscles: Muscle[] = [];
  equipment: Equipment[] = [];

  constructor(private exerciseService: ExerciseService) { }

  async ngOnInit(): Promise<void> {
    this.categories = this.exerciseService.categories;
    this.muscles = this.exerciseService.muscles;
    this.equipment = this.exerciseService.equipment;
    this.exercises = await this.exerciseService.loadExercises();
  }

}

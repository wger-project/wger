import { Component, OnInit } from '@angular/core';
import {ExerciseService} from '../exercise.service';
import {Category} from '../models/category.model';
import {Equipment} from '../models/equipment.model';
import {Exercise} from '../models/exercise.model';

@Component({
  selector: 'app-exercise-list',
  templateUrl: './exercise-list.component.html',
  styleUrls: ['./exercise-list.component.css']
})
export class ExerciseListComponent implements OnInit {
  exercises: Exercise[] = [];
  categories: Category[] = [];
  equipment: Equipment[] = [];

  /**
   Starting page for the pagination
   */
  page = 1;

  /**
   * number of elements per page. In order to "fill" the pages, this should
   * to be a multiple of 3, since there are 3 exercises per row.
   */
  pageSize = 12;

  /**
   * Number of pages shown before the ellipsis
   */
  maxPageShown = 7;

  constructor(private exerciseService: ExerciseService) { }

  ngOnInit(): void {
    this.getExercises();
    this.categories = this.exerciseService.categories;
    this.equipment = this.exerciseService.equipment;
  }

  async getExercises(): Promise<void> {
    this.exercises = await this.exerciseService.loadExercises();
  }

  async loadExercise(id: number): Promise<void> {

    const tmp = await this.exerciseService.getExercise(id);
    //console.log(tmp);
  }
}

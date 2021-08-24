import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Params} from '@angular/router';
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
  allExercises: Exercise[] = [];
  exercises: Exercise[] = [];
  categories: Category[] = [];
  equipment: Equipment[] = [];

  selectedCategory: number | null = null;
  selectedEquipment: number[] = [];

  language: string = 'en';

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


  constructor(private exerciseService: ExerciseService,
              private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.getExercises();
    this.categories = this.exerciseService.categories;
    this.equipment = this.exerciseService.equipment;

    this.route.params
      .subscribe(
        (params: Params) => {
          this.language = params.lang;
        }
      );
  }

  /*
   * Sets the given category ID as the currently selected one
   */
  setSelectedCategory(id: number | null) {
    this.selectedCategory = id;
    this.filterExercises();
  }

  /*
   * Adds or removes the given equipment ID from the list of selected oness
   */
  toggleSelectedEquipment(id: number) {
    const index = this.selectedEquipment.indexOf(id);

    if (index < 0) {
      this.selectedEquipment.push(id);
    } else {
      this.selectedEquipment.splice(index, 1);
    }

    this.filterExercises();
  }

  /*
   * Loads initial exercise list from the server
   */
  async getExercises(): Promise<void> {
    this.exercises = await this.exerciseService.loadExercises();
    this.allExercises = this.exercises.slice();
  }

  /*
   * Filter exercises based on the current selected equipments and category
   */
  filterExercises() {
    let out = this.allExercises.slice();

    if (this.selectedCategory != null) {
      out = out.filter(exercise => exercise.category.id === this.selectedCategory);
    }

    if (this.selectedEquipment.length > 0) {
      out = out.filter(exercise => exercise.equipment.findIndex(equipment =>
        this.selectedEquipment.indexOf(equipment.id) !== -1
      ) !== -1);
    }

    this.exercises = out;
  }
}

/*
 * This file is part of wger Workout Manager <https://github.com/wger-project>.
 * Copyright (C) 2020, 2021 wger Team
 *
 * wger Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * wger Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import {Component, Input, OnInit} from '@angular/core';
import {FormArray, FormBuilder, FormControl, FormGroup, Validators} from '@angular/forms';
import {ExerciseService} from '../exercise.service';
import {Category} from '../models/category.model';
import {Equipment} from '../models/equipment.model';
import {Exercise} from '../models/exercise.model';
import {Muscle} from '../models/muscle.model';

@Component({
  selector: 'app-exercise-edit',
  templateUrl: './exercise-edit.component.html',
  styleUrls: ['./exercise-edit.component.css']
})
export class ExerciseEditComponent implements OnInit {

  @Input() exercise!: Exercise;

  group!: FormGroup;
  categories: Category[] = [];
  muscles: Muscle[] = [];
  equipment: Equipment[] = [];

  constructor(private exerciseService: ExerciseService,
              private formBuilder: FormBuilder) {

  }

  ngOnInit(): void {
    this.categories = this.exerciseService.categories;
    this.muscles = this.exerciseService.muscles;
    this.equipment = this.exerciseService.equipment;

    this.initForm();
  }


  get musclesFormArray() {
    return this.group.controls.muscles as FormArray;
  }

  get musclesSecondaryFormArray() {
    return this.group.controls.musclesSecondary as FormArray;
  }

  get equipmentFormArray() {
    return this.group.controls.equipment as FormArray;
  }

  private addCheckboxes() {


    // Equipment
    this.equipment.forEach((value) => {
      this.equipmentFormArray.push(new FormControl(!!this.exercise.equipment.find(value1 => value1.id == value.id)));
    });

    // Muscles
    this.muscles.forEach((value) => {
      this.musclesFormArray.push(new FormControl(!!this.exercise.muscles.find(value1 => value1.id == value.id)));
    });

    // Secondary Muscles
    this.muscles.forEach((value) => {
      this.musclesSecondaryFormArray.push(new FormControl(!!this.exercise.musclesSecondary.find(value1 => value1.id == value.id)));
    });
  }


  onSubmit() {

    //console.log(this.group.value);

    const selectedEquipmentIds = this.group.value.equipment
      .map((checked: boolean, i: number) => checked ? this.equipment[i].id : null)
      .filter((v: null) => v !== null);

    //console.log(selectedEquipmentIds);

    const selectedMusclesIds = this.group.value.muscles
      .map((checked: boolean, i: number) => checked ? this.muscles[i].id : null)
      .filter((v: null) => v !== null);

    //console.log(selectedMusclesIds);

    const selectedSecondaryMusclesIds = this.group.value.musclesSecondary
      .map((checked: boolean, i: number) => checked ? this.muscles[i].id : null)
      .filter((v: null) => v !== null);

    //console.log(selectedSecondaryMusclesIds);


    //if (this.editMode) {
    if (this.exercise.id != null) {
      this.exerciseService.updateExercise(this.group.value);
    } else {
      this.exerciseService.addExercise(this.group.value);
    }


  }

  private initForm() {

    this.group = this.formBuilder.group({
      name: this.exercise.name,
      description: this.exercise.description,
      category: this.exercise.category.id,
      muscles: new FormArray([]),
      musclesSecondary: new FormArray([]),
      equipment: new FormArray([]),
    });

    this.addCheckboxes();
  }


}

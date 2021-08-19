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

import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';
import {Category} from './category.model';
import {Comment} from './comment.model';
import {Equipment} from './equipment.model';
import {ExerciseImage} from './image.model';
import {Muscle} from './muscle.model';

export class Exercise {
  category!: Category;
  categoryId: number;
  muscles: Muscle[] = [];
  musclesIds: number[] = [];
  musclesSecondary: Muscle[] = [];
  musclesSecondaryIds: number[] = [];
  equipment: Equipment[] = [];
  equipmentIds: number[] = [];
  images: ExerciseImage[] = [];
  comments: Comment[] = [];
  license: number;
  licenseAuthor: string;
  variations: number[];

  constructor(public id: number,
              public uuid: string,
              public name: string,
              public date: Date,
              public description: string,
              category: number,
              muscles: number[],
              musclesSecondary: number[],
              equipment: number[],
              license: number,
              licenseAuthor: string,
              variations: number[]) {
    this.categoryId = category;
    this.musclesIds = muscles;
    this.musclesSecondaryIds = musclesSecondary;
    this.equipmentIds = equipment;
    this.license = license;
    this.licenseAuthor = licenseAuthor;
    this.variations = variations;
  }
}


@Injectable({
  providedIn: 'root',
})
export class ExerciseAdapter implements Adapter<Exercise> {
  fromJson(item: any): Exercise {
    return new Exercise(
      item.id,
      item.uuid,
      item.name,
      new Date(item.creation_date),
      item.description,
      item.category,
      item.muscles,
      item.muscles_secondary,
      item.equipment,
      item.license,
      item.license_author,
      item.variations
      );
  }

  /**
   * Don't return all properties, since not all items can be updated (they would
   * be ignored by the server, but it's better to not send too much anyway)
   */
  toJson(item: Exercise): any {

    return {
      id: item.id,
      name: item.name,
      description: item.description,
      category: item.categoryId,
      muscles: item.musclesIds,
      muscles_secondary: item.musclesSecondaryIds,
      equipment: item.equipmentIds
    };
  }
}


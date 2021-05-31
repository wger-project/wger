import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';
import {Category} from './category.model';
import {Equipment} from './equipment.model';
import {ExerciseImage} from './image.model';
import {Muscle} from './muscle.model';

export class Exercise {
  id: number;
  uuid: string;
  name: string;
  date: Date;
  description: string;
  category!: Category;
  categoryId: number;
  muscles: Muscle[] = [];
  musclesIds: number[] = [];
  musclesSecondary: Muscle[] = [];
  musclesSecondaryIds: number[] = [];
  equipment: Equipment[] = [];
  equipmentIds: number[] = [];
  images: ExerciseImage[] = [];
  license: number;
  licenseAuthor: string;
  variations: number[];

  constructor(id: number,
              uuid: string,
              name: string,
              date: Date,
              description: string,
              category: number,
              muscles: number[],
              musclesSecondary: number[],
              equipment: number[],
              license: number,
              licenseAuthor: string,
              variations: number[]) {
    this.id = id;
    this.uuid = uuid;
    this.name = name;
    this.date = date;
    this.description = description;
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


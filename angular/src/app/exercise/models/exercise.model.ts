import {Category} from './category.model';
import {Equipment} from './equipment.model';
import {ExerciseImage} from './image.model';
import {Muscle} from './muscle.model';

export interface Exercise {
  id: number;
  uuid: string;
  name: string;
  description: string;
  category: number;
  muscles: number[];
  muscles_secondary: number[];
  equipment: number[];
  license: number;
  license_author: string;
  variations: number[];
}

export interface ExerciseInfo {
  id: number;
  name: string;
  description: string;
  category: Category[];
  muscles: Muscle[];
  muscles_secondary: Muscle[];
  equipment: Equipment[];
  images: ExerciseImage[];
}

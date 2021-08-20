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


import {Category} from '../models/category.model';
import {Exercise} from '../models/exercise.model';

export const category1 = new Category(1, 'Arms');
export const category2 = new Category(2, 'Back');
export const category3 = new Category(3, 'Legs');


export const exercise1 = new Exercise(1,
  'abcd',
  'Cool exercise',
  new Date(2021, 5, 10),
  'Take the weight, move it. ',
  1,
  [1, 2, 3],
  [5, 6],
  [1, 8],
  2,
  'author',
  [2]);

exercise1.category = category1;

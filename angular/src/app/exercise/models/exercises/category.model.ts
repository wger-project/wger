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
import {Adapter} from '../../../core/adapter';

export class Category{

  constructor(
    public id: number,
    public name: string
  ) { }
}

@Injectable({
  providedIn: 'root',
})
export class CategoryAdapter implements Adapter<Category> {
  fromJson(item: any): Category {
    return new Category(
      item.id,
      item.name
    );
  }

  toJson(item: Category): any {
    return {
      id: item.id,
      name: item.name,
    };
  }
}

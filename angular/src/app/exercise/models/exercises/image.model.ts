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

export class ExerciseImage{

  constructor(
    public id: number,
    public uuid: string,
    public url: string,
    public isMain: boolean) {
  }
}

@Injectable({
  providedIn: 'root',
})
export class ExerciseImageAdapter implements Adapter<ExerciseImage> {
  fromJson(item: any): ExerciseImage {
    return new ExerciseImage(
      item.id,
      item.uuid,
      item.image,
      item.is_main
    );
  }

  // TODO: when uploading an image we have to send the file
  toJson(item: ExerciseImage): any {
    return {
      id: item.id,
      image: item.url,
      is_front: item.isMain
    };
  }
}

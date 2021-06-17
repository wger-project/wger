import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';
import {Muscle} from './muscle.model';

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

import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';

export class Muscle {
  id: number;
  name: string;
  isFront: boolean;

  constructor(id: number, name: string, isFront: boolean) {
    this.id = id;
    this.name = name;
    this.isFront = isFront;
  }

}

@Injectable({
  providedIn: 'root',
})
export class MuscleAdapter implements Adapter<Muscle> {
  fromJson(item: any): Muscle {
    return new Muscle(
      item.id,
      item.name,
      item.is_front
    );
  }

  toJson(item: Muscle): any {
    return {
      id: item.id,
      name: item.name,
      is_front: item.isFront
    };
  }
}

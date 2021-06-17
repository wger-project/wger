import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';
import {Muscle} from './muscle.model';

export class Equipment{

  constructor(
    public id: number,
    public name: string) { }
}

@Injectable({
  providedIn: 'root',
})
export class EquipmentAdapter implements Adapter<Equipment> {
  fromJson(item: any): Equipment {
    return new Equipment(
      item.id,
      item.name,
    );
  }

  toJson(item: Equipment): any {
    return {
      id: item.id,
      name: item.name,
    };
  }
}

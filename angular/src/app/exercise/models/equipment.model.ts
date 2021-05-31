import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';
import {Muscle} from './muscle.model';

export class Equipment{
  id: number;
  name: string;

  constructor(id: number, name: string) {
    this.id = id;
    this.name = name;
  }
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

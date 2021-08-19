import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';

export class Equipment{
  constructor(
    public id: number,
    public name: string) { }

  toString() {
    return this.name;
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

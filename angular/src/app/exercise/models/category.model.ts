import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';

export class Category{

  constructor(
    public id: number,
    public name: string
  ) { }

  toString() {
    return this.name;
  }
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

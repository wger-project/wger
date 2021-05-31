import {Injectable} from '@angular/core';
import {Adapter} from '../../core/adapter';

export class Category{
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

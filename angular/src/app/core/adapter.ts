export interface Adapter<T> {
  fromJson(item: any): T;

  toJson(item: T): any;
}

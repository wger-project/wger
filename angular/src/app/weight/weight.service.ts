import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import {WeightAdapter, WeightEntry} from './models/weight.model';


@Injectable({
  providedIn: 'root',
})
export class WeightService {
  weightEntryUrl = environment.apiUrl + 'weightentry/';

  entries: WeightEntry[] = [];

  constructor(private http: HttpClient,
              private weightAdapter: WeightAdapter,
  ) {
  }

  sortEntries() {
    this.entries.sort((a, b) => (a.date > b.date ? -1 : 1));
  }


  async loadWeightEntries(): Promise<WeightEntry[]> {
    const data = await this.http.get<any>(this.weightEntryUrl, {params: {limit: 500}, headers: environment.headers}).toPromise();

    for (const weightData of data.results) {
      this.entries.push(this.weightAdapter.fromJson(weightData));
    }
    this.sortEntries();
    return this.entries;
  }


  /**
   * Updates an existing weight entry
   *
   * @param weight a [WeightEntry] instance
   */
  updateWeightEntry(weight: WeightEntry) {
    this.http.patch<any>(this.weightEntryUrl + weight.id + '/', this.weightAdapter.toJson(weight), {
      headers: environment.headers
    }).subscribe(value => { });
  }

  /**
   * Inserts a new weight entry into the database
   *
   * @param data: the weight entry data
   */
  addWeightEntry(data: {weight: number, date: Date}) {
    this.http.post<any>(this.weightEntryUrl, data, {
      headers: environment.headers
    }).subscribe(value => {
      this.entries.push(this.weightAdapter.fromJson(value));
      this.sortEntries();
    });
  }

  /**
   * Deletes the weight entry with the given ID
   *
   * @param id: ID of the weight entry
   */
  deleteWeightEntry(id: number) {

    this.http.delete<any>(this.weightEntryUrl + id + '/', {
      headers: environment.headers
    }).subscribe();


    this.entries.forEach((value: WeightEntry, index: number) => {
      if (value.id == id) {
        this.entries.splice(index, 1);
      }
    });
  }
}

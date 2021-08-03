import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Subject} from 'rxjs';
import {environment} from '../../environments/environment';
import {AuthService} from '../core/auth.service';
import {WeightAdapter, WeightEntry} from './models/weight.model';


@Injectable({
  providedIn: 'root',
})
export class WeightService {
  weightEntryUrl = environment.apiUrl + 'weightentry/';
  weightChanged = new Subject<WeightEntry[]>();

  private entries: WeightEntry[] = [];

  constructor(private http: HttpClient,
              private weightAdapter: WeightAdapter,
              private authService: AuthService,
  ) {
    this.loadWeightEntries();
  }

  get weightEntries() {
    return this.entries.slice();
  }


  /**
   * Sorts weight entries by date.
   *
   * While they are already sorted server side, this is necessary, e.g. when
   * adding or deleting
   */
  sortEntries() {
    this.entries.sort((a, b) => (a.date > b.date ? -1 : 1));
  }


  loadWeightEntries(): WeightEntry[] {

    const data = this.http.get<any>(this.weightEntryUrl,
      {params: {limit: 500}, headers: this.authService.headers}).subscribe(data => {
      for (const weightData of data.results) {
        this.entries.push(this.weightAdapter.fromJson(weightData));
      }
      this.sortEntries();
      this.weightChanged.next(this.weightEntries);
    });

    return this.weightEntries;
  }


  /**
   * Updates an existing weight entry
   *
   * @param weightData: weight entry data object
   * @param id: id of the weight entry data to update
   */
  updateWeightEntry(weightData: any, id: number) {

    this.http.patch<any>(this.weightEntryUrl + id + '/',
      weightData, {
        headers: this.authService.headers
      }).subscribe(value => {

      const index = this.findIndexById(id);
      this.entries[index] = this.weightAdapter.fromJson(value);
      this.sortEntries();
      this.weightChanged.next(this.weightEntries);
    });
  }

  /**
   * Inserts a new weight entry into the database
   *
   * @param data: the weight entry data
   */
  addWeightEntry(data: { weight: number, date: Date }) {
    this.http.post<any>(this.weightEntryUrl, data, {
      headers: this.authService.headers
    }).subscribe(value => {
      this.entries.push(this.weightAdapter.fromJson(value));
      this.sortEntries();
      this.weightChanged.next(this.weightEntries);
    });
  }

  /**
   * Deletes the weight entry with the given ID
   *
   * @param id: ID of the weight entry
   */
  deleteWeightEntry(id: number) {
    this.http.delete<any>(this.weightEntryUrl + id + '/', {
      headers: this.authService.headers
    }).subscribe(value => {
      this.entries.forEach((value: WeightEntry, index: number) => {
        if (value.id == id) {
          this.entries.splice(index, 1);
        }
      });

      this.weightChanged.next(this.weightEntries);
    });
  }

  /**
   * Finds an entry by its ID
   *
   * @param id: ID of the weight entry
   */
  findById(id: number) {
    return this.entries.find(value => value.id == id);
  }

  /**
   * Finds the index of a weight entry by its ID
   *
   * @param id: ID of the weight entry
   */
  findIndexById(id: number) {
    return this.entries.findIndex(value => value.id == id);
  }

}

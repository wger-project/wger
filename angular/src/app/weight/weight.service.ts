import {HttpClient} from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';
import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import {WeightAdapter, WeightEntry} from '../exercise/models/weight/weight.model';


@Injectable({
  providedIn: 'root',
})
export class WeightService {
  weightEntryUrl = environment.apiUrl + 'weightentry';

  entries: WeightEntry[] = [];

  constructor(private http: HttpClient,
              private weightAdapter: WeightAdapter,
              ) {
  }



  async loadWeightEntries(): Promise<WeightEntry[]> {
    const data = await this.http.get<any>(this.weightEntryUrl, {params: {limit: 10}, headers: new HttpHeaders({
        'Content-Type':  'application/json',
        Authorization: 'Token d2e9db08e3c1eea2adb62e60e75fa8922af8bbd5'
      })}).toPromise();


    for (const weightData of data.results) {
      console.log(weightData);

      this.entries.push(this.weightAdapter.fromJson(weightData));
    }

    return this.entries;
  }

  updateWeightEntry(data: any) {

  }
  addWeightEntry(data: any) {

  }
}

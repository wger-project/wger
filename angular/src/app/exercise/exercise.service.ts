import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {WgerApiResponse} from '../core/wger-response.model';
import {Exercise} from './models/exercise.model';


@Injectable({
  providedIn: 'root',
})
export class ExerciseService {
  url = environment.apiUrl + 'exercise';

  constructor(private http: HttpClient) {
  }

  getExercises(): Observable<WgerApiResponse<Exercise>> {
    return this.http.get<WgerApiResponse<Exercise>>(this.url);
  }
}

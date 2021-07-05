import {HttpHeaders} from '@angular/common/http';
import {Environment} from './environment.interface';


export const environment: Environment = {
  production: false,
  name: 'prod',
  apiUrl: '/api/v2/',
  headers: new HttpHeaders({
    'Content-Type':  'application/json',
  }),
};

import {HttpHeaders} from '@angular/common/http';
import {Environment} from './environment.interface';

/**
 * During development it is often easier to develop only in an angular context
 * while during production, it is not necessary to set a host
 */
export const environment: Environment = {
  production: false,
  name: 'dev',
  apiUrl: 'http://localhost:8000/api/v2/',
  headers: new HttpHeaders({
    'Content-Type':  'application/json',
    Authorization: 'Token d2e9db08e3c1eea2adb62e60e75fa8922af8bbd5'
  }),
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.

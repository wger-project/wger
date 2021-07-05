import {HttpHeaders} from '@angular/common/http';


export interface Environment {
  production: boolean;
  name: string;
  apiUrl: string;
  headers: HttpHeaders
}


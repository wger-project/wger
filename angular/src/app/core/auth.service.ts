import {HttpHeaders} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';

/**
 * Helper service that sets the appropriate headers
 *
 * During local development we use the Token defined in the dev environment
 * but on the wger application, we need to pass the CSRF value in the header
 */
@Injectable({
  providedIn: 'root',
})
export class AuthService {

  DJANGO_CSRF_COOKIE = 'csrftoken';

  constructor() {
  }

  // from https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
  getCookie(name: string) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  get headers(): HttpHeaders {
    const csrf_cookie = this.getCookie(this.DJANGO_CSRF_COOKIE);
    let headers = environment.headers;

    if(csrf_cookie != undefined)
    {
      headers = headers.set('X-CSRFToken', csrf_cookie);
    }
    return headers;
  }


}

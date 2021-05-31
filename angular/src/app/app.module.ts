import {HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppComponent} from './app.component';
import {ExerciseDetailComponent} from './exercise/exercise-detail/exercise-detail.component';
import { ExerciseListComponent } from './exercise/exercise-list/exercise-list.component';

@NgModule({
  declarations: [
    AppComponent,
    ExerciseDetailComponent,
    ExerciseListComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

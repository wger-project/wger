/*
 * This file is part of wger Workout Manager <https://github.com/wger-project>.
 * Copyright (C) 2020, 2021 wger Team
 *
 * wger Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * wger Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import {HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {NgxChartsModule} from '@swimlane/ngx-charts';

import {AppComponent} from './app.component';
import {ExerciseDetailComponent} from './exercise/exercise-detail/exercise-detail.component';
import { ExerciseListComponent } from './exercise/exercise-list/exercise-list.component';
import { ExerciseEditComponent } from './exercise/exercise-edit/exercise-edit.component';
import {ExerciseService} from './exercise/exercise.service';
import {WeightListComponent} from './weight/weight-list/weight-list.component';
import { WeightDetailComponent } from './weight/weight-detail/weight-detail.component';
import { WeightEditComponent } from './weight/weight-edit/weight-edit.component';
import { WeightChartComponent } from './weight/weight-chart/weight-chart.component';

@NgModule({
  declarations: [
    AppComponent,
    ExerciseDetailComponent,
    ExerciseListComponent,
    ExerciseEditComponent,

    WeightListComponent,
    WeightDetailComponent,
    WeightEditComponent,
    WeightChartComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule,
    NgxChartsModule,
    BrowserAnimationsModule
  ],
  providers: [ExerciseService],
  bootstrap: [AppComponent]
})
export class AppModule { }

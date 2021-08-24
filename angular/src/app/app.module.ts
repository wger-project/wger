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

import {APP_BASE_HREF} from '@angular/common';
import {HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterModule, Routes} from '@angular/router';
import {
  NgbAccordionModule,
  NgbDropdownModule,
  NgbModalModule,
  NgbPaginationModule
} from '@ng-bootstrap/ng-bootstrap';
import {NgxChartsModule} from '@swimlane/ngx-charts';

import {AppComponent} from './app.component';
import {ExerciseAddComponent} from './exercise/exercise-add/exercise-add.component';
import {ExerciseDetailComponent} from './exercise/exercise-detail/exercise-detail.component';
import {ExerciseEditComponent} from './exercise/exercise-edit/exercise-edit.component';
import {ExerciseListComponent} from './exercise/exercise-list/exercise-list.component';
import {ExerciseService} from './exercise/exercise.service';
import {WeightChartComponent} from './weight/weight-chart/weight-chart.component';
import {WeightDetailComponent} from './weight/weight-detail/weight-detail.component';
import {WeightEditComponent} from './weight/weight-edit/weight-edit.component';
import {WeightListComponent} from './weight/weight-list/weight-list.component';
import {WeightService} from './weight/weight.service';
import { ExercisePreviewComponent } from './exercise/exercise-preview/exercise-preview.component';

const appRoutes: Routes = [
  {path: '', component: WeightListComponent},
  {path: ':lang/dashboard', component: WeightChartComponent},

  // Exercises
  {path: ':lang/exercise/overview', component: ExerciseListComponent},
  {path: ':lang/exercise/:id/view', component: ExerciseDetailComponent},
  {path: ':lang/exercise/add', component: ExerciseAddComponent},
  {path: ':lang/exercise/:id/view/:slug', component: ExerciseDetailComponent},

  //  Weight
  {path: ':lang/weight/overview', component: WeightListComponent},
];

@NgModule({
  declarations: [
    AppComponent,
    ExerciseDetailComponent,
    ExerciseEditComponent,
    ExerciseListComponent,
    ExerciseAddComponent,

    WeightChartComponent,
    WeightDetailComponent,
    WeightEditComponent,
    WeightListComponent,
    ExercisePreviewComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    HttpClientModule,

    // Angular bootstrap
    NgbDropdownModule,
    NgbModalModule,
    NgbPaginationModule,
    NgbAccordionModule,
    //NgbModule,


    // Charts
    NgxChartsModule,

    ReactiveFormsModule,
    RouterModule.forRoot(appRoutes),
  ],
  providers: [
    ExerciseService,
    WeightService,
    {provide: APP_BASE_HREF, useValue: '/'}
  ],
  bootstrap: [
    AppComponent,
  ],
})
export class AppModule { }

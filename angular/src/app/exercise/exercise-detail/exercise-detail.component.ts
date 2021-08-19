import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Params} from '@angular/router';
import {ExerciseService} from '../exercise.service';
import {Exercise} from '../models/exercises/exercise.model';

@Component({
  selector: 'app-exercise-detail',
  templateUrl: './exercise-detail.component.html',
  styleUrls: ['./exercise-detail.component.css']
})
export class ExerciseDetailComponent implements OnInit{

  id?: number;
  exercise!: Exercise;

  constructor(private exerciseService: ExerciseService,
              private route: ActivatedRoute) {
  }

  async ngOnInit(): Promise<void> {

    this.route.params
      .subscribe(
        (params: Params) => {
          this.id = params.id;
        }
      );

    if(this.id != null) {
      this.exercise = await this.exerciseService.loadExerciseById(this.id);
    }
  }
}

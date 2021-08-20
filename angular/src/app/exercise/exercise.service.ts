import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';
import {WgerApiResponse} from '../core/wger-response.model';
import {Category, CategoryAdapter} from './models/category.model';
import {CommentAdapter} from './models/comment.model';
import {Equipment, EquipmentAdapter} from './models/equipment.model';
import {Exercise, ExerciseAdapter} from './models/exercise.model';
import {ExerciseImageAdapter} from './models/image.model';
import {Muscle, MuscleAdapter} from './models/muscle.model';

@Injectable({
  providedIn: 'root',
})
export class ExerciseService {
  exerciseUrl = environment.apiUrl + 'exercise';
  exerciseInfoUrl = environment.apiUrl + 'exerciseinfo';
  categoryUrl = environment.apiUrl + 'exercisecategory';
  muscleUrl = environment.apiUrl + 'muscle';
  equipmentUrl = environment.apiUrl + 'equipment';

  exercises: Exercise[] = [];
  categories: Category[] = [];
  muscles: Muscle[] = [];
  equipment: Equipment[] = [];

  constructor(private http: HttpClient,
              private exerciseAdapter: ExerciseAdapter,
              private categoryAdapter: CategoryAdapter,
              private muscleAdapter: MuscleAdapter,
              private equipmentAdapter: EquipmentAdapter,
              private exerciseImageAdapter: ExerciseImageAdapter,
              private commentAdapter: CommentAdapter,
  ) {
    this.loadBaseData();
  }

  loadBaseData(): void {
    // Load all categories
    this.http.get<WgerApiResponse<Category>>(this.categoryUrl).subscribe(data => {
      for (const categoryData of data.results) {
        this.categories.push(this.categoryAdapter.fromJson(categoryData));
      }
    });

    // Load all muscles
    this.http.get<WgerApiResponse<Muscle>>(this.muscleUrl).subscribe(data => {
      for (const muscleData of data.results) {
        this.muscles.push(this.muscleAdapter.fromJson(muscleData));
      }
    });

    // Load all equipment
    this.http.get<WgerApiResponse<Equipment>>(this.equipmentUrl).subscribe(data => {
      for (const equipmentData of data.results) {
        this.equipment.push(this.equipmentAdapter.fromJson(equipmentData));
      }
    });
  }

  loadExerciseFromData(exerciseData: any): Exercise {
    // Exercise itself
    const exercise = this.exerciseAdapter.fromJson(exerciseData);

    // Category
    exercise.category = this.categoryAdapter.fromJson(exerciseData.category);

    // Muscles
    for (const muscleData of exerciseData.muscles) {
      exercise.muscles.push(this.muscleAdapter.fromJson(muscleData));
      //exercise.addMuscle(this.muscleAdapter.fromJson(muscleData));
    }
    for (const muscleData of exerciseData.muscles_secondary) {
      exercise.musclesSecondary.push(this.muscleAdapter.fromJson(muscleData));
      //exercise.addMuscleSecondary(this.muscleAdapter.fromJson(muscleData));
    }

    // Equipment
    for (const equipmentData of exerciseData.equipment) {
      exercise.equipment.push(this.equipmentAdapter.fromJson(equipmentData));
      //exercise.addEquipment(this.equipmentAdapter.fromJson(equipmentData));
    }

    // Images
    for (const imageData of exerciseData.images) {
      exercise.images.push(this.exerciseImageAdapter.fromJson(imageData));
    }

    // Comments
    for (const commentData of exerciseData.comments) {
      exercise.comments.push(this.commentAdapter.fromJson(commentData));
    }

    return exercise;
  }


  /*
   * Loads an exercise from the server by it's ID
   */
  async loadExerciseById(id: number): Promise<Exercise> {
    const data = await this.http.get<any>(this.exerciseInfoUrl + '/' + id).toPromise();
    return this.loadExerciseFromData(data);
  }

  async loadExercises(): Promise<Exercise[]> {
    const data = await this.http.get<any>(this.exerciseInfoUrl, {params: {limit: 50}}).toPromise();

    this.exercises = [];

    for (const exerciseData of data.results) {
      this.exercises.push(this.loadExerciseFromData(exerciseData));
    }

    return this.exercises;
  }

  getExercise(id: number): Exercise {
    return this.exercises.find(value => value.id === id)!;
  }

  getCategoryById(id: number): Category {
    return this.categories.find(value => value.id === id)!;
  }

  getMuscleById(id: number): Muscle {
    return this.muscles.find(value => value.id === id)!;
  }

  getEquipmentById(id: number): Equipment {
    return this.equipment.find(value => value.id === id)!;
  }

  updateExercise(data: any) {
  }

  addExercise(data: any) {
  }
}

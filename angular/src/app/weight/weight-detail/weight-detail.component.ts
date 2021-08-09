import {Component, Input} from '@angular/core';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-detail',
  templateUrl: './weight-detail.component.html',
  styleUrls: ['./weight-detail.component.css']
})
export class WeightDetailComponent {

  @Input() entry!: WeightEntry;
  @Input() weightDiff?: number;
  @Input() dayDiff?: number;
  showForm = false;

  constructor(private weightService: WeightService) {
  }

  toggleForm() {
    this.showForm = !this.showForm;
  }

  /**
   * The form should be closed
   */
  onFormCancelled() {
    this.showForm = false;
  }



  /**
   * Deletes this weight entry
   */
  deleteEntry() {
    this.weightService.deleteWeightEntry(this.entry.id!);
  }


}

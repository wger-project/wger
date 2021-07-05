import {Component, Input, OnInit} from '@angular/core';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-detail',
  templateUrl: './weight-detail.component.html',
  styleUrls: ['./weight-detail.component.css']
})
export class WeightDetailComponent implements OnInit {

  @Input() entry!: WeightEntry;

  constructor(private weightService: WeightService) {
  }

  ngOnInit(): void {
  }

  /**
   * Deletes this weight entry
   */
  deleteEntry() {
    this.weightService.deleteWeightEntry(this.entry.id);
  }


}

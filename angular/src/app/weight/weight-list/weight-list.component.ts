import { Component, OnInit } from '@angular/core';
import {WeightEntry} from '../../exercise/models/weight/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-list',
  templateUrl: './weight-list.component.html',
  styleUrls: ['./weight-list.component.css']
})
export class WeightListComponent implements OnInit {
  weightEntries: WeightEntry[] = [];

  constructor(private service: WeightService) { }

  ngOnInit(): void {
    this.getWeightEntries();
  }

  async getWeightEntries(): Promise<void> {
    this.weightEntries = await this.service.loadWeightEntries();
  }
}

import {Component, Input, OnInit} from '@angular/core';
import {WeightEntry} from '../../exercise/models/weight/weight.model';

@Component({
  selector: 'app-weight-detail',
  templateUrl: './weight-detail.component.html',
  styleUrls: ['./weight-detail.component.css']
})
export class WeightDetailComponent implements OnInit {

  @Input() entry!: WeightEntry;

  constructor() { }

  ngOnInit(): void {
  }

}

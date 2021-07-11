import { Component, OnInit } from '@angular/core';
import {NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-list',
  templateUrl: './weight-list.component.html',
  styleUrls: ['./weight-list.component.css']
})
export class WeightListComponent implements OnInit {
  weightEntries: WeightEntry[] = [];

  /**
  Starting page for the pagination
   */
  page = 1;

  /**
   * number of elements per page
   */
  pageSize = 10;

  /**
   * Number of pages shown before the ellipsis
   */
  maxPageShown = 7;

  constructor(
    private service: WeightService,
    private modalService: NgbModal
  ) { }

  ngOnInit(): void {
    this.getWeightEntries();
  }

  async getWeightEntries(): Promise<void> {
    this.weightEntries = await this.service.loadWeightEntries();
  }

  open(content: any) {
    this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'}).result.then((result) => {
      console.log(`Closed with: ${result}`);
    }, (reason) => {
      console.log(`Dismissed`);
    });
  }
}

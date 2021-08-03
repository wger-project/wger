import {Component, OnDestroy, OnInit} from '@angular/core';
import {NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {Subscription} from 'rxjs';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-list',
  templateUrl: './weight-list.component.html',
  styleUrls: ['./weight-list.component.css']
})
export class WeightListComponent implements OnInit, OnDestroy {
  weightEntriesProcessed: { entry: WeightEntry, weightDiff: number, dayDiff: number }[] = [];
  private subscription!: Subscription;

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
  ) {
  }

  ngOnInit(): void {
    this.subscription = this.service.weightChanged.subscribe(
      (newEntries: WeightEntry[]) => {
        this.processWeightEntries(newEntries);
      }
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  /**
   * Processes the weight entries and calculates the difference in days between
   * entries.
   *
   * This could potentially be moved to the model
   */
  processWeightEntries(newEntries: WeightEntry[]): void {
    this.weightEntriesProcessed = [];
    const nrOfEntries = newEntries.length;
    newEntries.forEach((currentEntry, index) => {

      // Newest entries are the first
      const prevIndex = index + 1;

      // Calculate the difference to the entry before
      const weightDiff = prevIndex < nrOfEntries ? currentEntry.weight - newEntries[prevIndex].weight : 0;
      const dayDiff = prevIndex < nrOfEntries ? (currentEntry.date.getTime() - newEntries[prevIndex].date.getTime()) / (1000 * 3600 * 24) : 0;

      this.weightEntriesProcessed.push({entry: currentEntry, weightDiff: weightDiff, dayDiff: dayDiff});
    });
  }

  openModal(content: any) {
    this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title'}).result.then((result) => {
      console.log(`Closed with: ${result}`);
    }, (reason) => {
      console.log(`Dismissed`);
    });
  }

  /**
   * The form should be closed
   */
  onFormCancelled() {
    this.modalService.dismissAll();
  }
}

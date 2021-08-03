import {Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {NgbModal} from '@ng-bootstrap/ng-bootstrap';
import {Subscription} from 'rxjs';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-chart',
  templateUrl: './weight-chart.component.html',
  styleUrls: ['./weight-chart.component.css']
})
export class WeightChartComponent implements OnInit, OnDestroy {

  // Chart options
  view: [number, number] = [700, 300];
  legend: boolean = false;
  showLabels: boolean = true;
  animations: boolean = true;
  xAxis: boolean = true;
  yAxis: boolean = true;
  showYAxisLabel: boolean = false;
  showXAxisLabel: boolean = false;
  timeline: boolean = true;
  autoScale = true;
  colorScheme = {
    domain: ['#266dd3']
  };

  data: any;

  private weightEntries: WeightEntry[] = [];

  selectedEntry!: WeightEntry;

  private subscription!: Subscription;

  @ViewChild('content') input!: ElementRef;

  constructor(
    private service: WeightService,
    private modalService: NgbModal,
  ) {
  }

  ngOnInit(): void {
    this.subscription = this.service.weightChanged.subscribe(
      (newEntries: WeightEntry[]) => {
        this.weightEntries = newEntries;
        this.processData();
      }
    );
  }


  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  private processData() {
    const out = this.weightEntries.map(entry => {
      return {name: entry.date, value: entry.weight, id: entry.id};
    });
    this.data = [{
      name: $localize`Weight`,
      series: out
    }];
  }


  onSelect(data: any): void {

    const entry = this.service.findById(data.id);
    if(entry === undefined) {
      return;
    }
    this.selectedEntry = entry;
    console.log(`Loaded entry ${entry.id}`);
    this.openModal(this.input);
  }

  onActivate(data: any): void {
    console.log('Activate', JSON.parse(JSON.stringify(data)));
  }

  onDeactivate(data: any): void {
    console.log('Deactivate', JSON.parse(JSON.stringify(data)));
  }

  /*
   * Open the modal allowing editing the entry
   */
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

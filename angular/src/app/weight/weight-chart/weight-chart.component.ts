import {Component, OnInit} from '@angular/core';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-chart',
  templateUrl: './weight-chart.component.html',
  styleUrls: ['./weight-chart.component.css']
})
export class WeightChartComponent implements OnInit {

  view: [number, number] = [700, 300];

  // options
  legend: boolean = false;
  showLabels: boolean = true;
  animations: boolean = true;
  xAxis: boolean = true;
  yAxis: boolean = true;
  showYAxisLabel: boolean = false;
  showXAxisLabel: boolean = false;
  //xAxisLabel: string = 'Date';
  //yAxisLabel: string = 'Weight';
  timeline: boolean = true;
  autoScale = true;

  colorScheme = {
    domain: ['#266dd3', '#E44D25', '#CFC0BB', '#7aa3e5', '#a8385d', '#aae3f5']
  };

  data : any


  constructor(private service: WeightService) {
  }

  async ngOnInit(): Promise<void> {

    // TODO: only load service data once
    await this.service.loadWeightEntries();

    const out: {name: Date, value: number}[] = this.service.entries.map(entry => {
      return {name: entry.date, value: entry.weight};
    });
    console.log(out);
    this.data = [{
      name: 'Weight',
      series: out
    }];

  }


  onSelect(data: any): void {
    console.log('Item clicked', JSON.parse(JSON.stringify(data)));
  }

  onActivate(data: any): void {
    console.log('Activate', JSON.parse(JSON.stringify(data)));
  }

  onDeactivate(data: any): void {
    console.log('Deactivate', JSON.parse(JSON.stringify(data)));
  }

}

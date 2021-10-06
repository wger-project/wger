import {HttpClientTestingModule} from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {NgxChartsModule} from '@swimlane/ngx-charts';
import {WeightService} from '../weight.service';

import { WeightChartComponent } from './weight-chart.component';

describe('WeightChartComponent', () => {
  let component: WeightChartComponent;
  let fixture: ComponentFixture<WeightChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WeightChartComponent ],
      imports: [HttpClientTestingModule],
      providers: [WeightService]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WeightChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

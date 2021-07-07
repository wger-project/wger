import {Component, Input, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {WeightEntry} from '../models/weight.model';
import {WeightService} from '../weight.service';

@Component({
  selector: 'app-weight-edit',
  templateUrl: './weight-edit.component.html',
  styleUrls: ['./weight-edit.component.css']
})
export class WeightEditComponent implements OnInit {

  @Input() weight?: WeightEntry;

  group!: FormGroup;

  constructor(private service: WeightService,
              private formBuilder: FormBuilder,
  ) { }

  ngOnInit(): void {

    if(!this.weight) {
      console.log("thi weight is not defined");
      this.weight = new WeightEntry(new Date(), 0);
    }

    this.initForm();
  }

  private initForm() {

    this.group = this.formBuilder.group({
      date: [this.weight!.date.toISOString().split('T')[0], Validators.required],
      weight: [
        this.weight!.weight,
        [Validators.required, Validators.min(30), Validators.max(300)],
      ],
    });
  }

  onSubmit() {

    if (this.group.invalid) {
      return;
    }

    this.weight!.weight = this.group.value.weight;
    this.weight!.date = this.group.value.date;


    if(this.weight?.id) {
      console.log('editing weight entry ' + this.weight.id);
      this.service.updateWeightEntry(this.weight);
    } else {
      console.log('adding new weight entry');
      this.service.addWeightEntry(this.group.value);
    }

    this.group.reset();
  }

}

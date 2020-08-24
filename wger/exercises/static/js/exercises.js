/*
 This file is part of wger Workout Manager.

 wger Workout Manager is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 wger Workout Manager is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 */

/*
 wger exercise functions
 */

'use strict';

/*
 D3js functions
 */

function wgerDrawWeightLogChart(data, divId) {
  var chartData;
  var legend;
  var minValues;
  var i;
  if (data.length) {
    legend = [];
    minValues = [];
    chartData = [];
    for (i = 0; i < data.length; i++) {
      chartData[i] = MG.convert.date(data[i], 'date');

      // Read the possible repetitions for the chart legend
      legend[i] = data[i][0].reps;

      // Read the minimum values for each repetition
      minValues[i] = d3.min(data[i], function (repetitionData) {
        return repetitionData.weight;
      });
    }

    MG.data_graphic({
      data: chartData,
      y_accessor: 'weight',
      min_y: d3.min(minValues),
      aggregate_rollover: true,
      full_width: true,
      top: 10,
      left: 30,
      right: 10,
      height: 200,
      legend: legend,
      target: '#svg-' + divId,
      colors: ['#204a87', '#4e9a06', '#ce5c00', '#5c3566', '#2e3436', '8f5902', '#a40000']
    });
  }
}

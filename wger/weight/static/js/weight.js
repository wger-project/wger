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
'use strict';

function modifyTimePeriod(data, pastNumberDays) {
  var filtered;
  var date;
  if (data.length) {
    if (pastNumberDays !== 'all') {
      date = new Date();
      date.setDate(date.getDate() - pastNumberDays);
      filtered = MG.clone(data).filter(function (value) {
        return value.date >= date;
      });
      return filtered;
    }
  }
  return data;
}

$(document).ready(function () {
  var url;
  var username;
  var chartParams;
  var weightChart;
  weightChart = {};
  chartParams = {
    animate_on_load: true,
    full_width: true,
    top: 10,
    left: 30,
    right: 10,
    show_secondary_x_label: true,
    xax_count: 10,
    target: '#weight_diagram',
    x_accessor: 'date',
    y_accessor: 'weight',
    min_y_from_data: true,
    colors: ['#3465a4']
  };

  username = $('#current-username').data('currentUsername');
  url = '/weight/api/get_weight_data/' + username;

  d3.json(url, function (json) {
    var data;
    if (json.length) {
      data = MG.convert.date(json, 'date');
      weightChart.data = data;

      // Plot the data
      chartParams.data = data;
      MG.data_graphic(chartParams);
    }
  });

  $('.modify-time-period-controls button').click(function () {
    var pastNumberDays = $(this).data('time_period');
    var data = modifyTimePeriod(weightChart.data, pastNumberDays);

    // change button state
    $(this).addClass('active').siblings().removeClass('active');
    if (data.length) {
      chartParams.data = data;
      MG.data_graphic(chartParams);
    }
  });
});


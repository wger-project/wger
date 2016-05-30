/*
 * This file is part of wger Workout Manager.
 *
 * wger Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * wger Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 */


/*
 * wger exercise functions
 */

"use strict";



/*
 * Highlight a muscle in the overview
 */
function highlight_muscle(element) {
    var div_id = $(element).data('target');
    var is_front = ($(element).data('isFront') == 'True') ? 'front' : 'back';
    var muscle_id = div_id.match(/\d+/);
    var muscle_name = $(element).data('name');

    // Reset all other highlighted muscles
    $('.muscle').removeClass('muscle-active');
    $('.muscle').addClass('muscle-inactive');

    // Hightligh the current one
    $(element).removeClass('muscle-inactive');
    $(element).addClass('muscle-active');

    // Set the corresponding background
    $('#muscle-system').css('background-image',
                            'url(/static/images/muscles/main/muscle-' + muscle_id + '.svg),'
                          + 'url(/static/images/muscles/muscular_system_' + is_front + '.svg)');

    // Show the corresponding exercises
    $('.exercise-list').hide();
    $('#' + div_id).show();
}

/*
 *
 * D3js functions
 *
 */

function draw_weight_log_chart(data, div_id, rep_i18n) {

    var legend = [];
    var min_values = [];
    var chart_data = [];
    for (var i = 0; i < data.length; i++) {
        chart_data[i] = MG.convert.date(data[i], 'date');

        // Read the possible repetitions for the chart legend
        legend[i] = data[i][0].reps;

        // Read the minimum values for each repetition
        min_values[i] = d3.min(data[i], function accessor (data) {
            return data.weight;
        });
    }

    MG.data_graphic({
        data: chart_data,
        y_accessor: 'weight',
        min_y: d3.min(min_values),
        aggregate_rollover: true,
        full_width: true,
        top: 10,
        left: 10,
        right: 10,
        height: 200,
        legend: legend,
        target: '#svg-' + div_id
    });
}


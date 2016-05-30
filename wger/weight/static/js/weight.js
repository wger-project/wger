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

"use strict";

$(document).ready(function () {

    var weight_chart = {};
    var chart_params = {
        animate_on_load: true,
        full_width: true,
        top: 10,
        left: 25,
        right: 10,
        height: 300,
        show_secondary_x_label: true,
        xax_count: 10,
        target: '#weight_diagram',
        x_accessor: 'date',
        y_accessor: 'weight',
        min_y_from_data: true,
        colors: ['#3465a4']
    }


    var username = $('#current-username').data('currentUsername');
    var url = "/weight/api/get_weight_data/" + username;

    d3.json(url, function (json) {

        var data =  MG.convert.date(json, 'date');
        weight_chart.data = data;

        // Plot the data
        chart_params.data = data;
        MG.data_graphic(chart_params);
    });

    $('.modify-time-period-controls button').click(function () {
        var past_n_days = $(this).data('time_period');
        var data = modify_time_period(weight_chart.data, past_n_days);

        // change button state
        $(this).addClass('active').siblings().removeClass('active');

        chart_params.data = data;
        MG.data_graphic(chart_params);
    });
});


function modify_time_period(data, past_n_days) {
    if (past_n_days !== 'all' || past_n_days !== '') {
        return MG.clone(data).slice(past_n_days * -1);
    }

    return data;
}


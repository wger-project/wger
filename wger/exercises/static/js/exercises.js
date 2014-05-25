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
function highlight_muscle(element, perms_exercises) {
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

    if (perms_exercises) {
        $('#muscle-edit-box').show();
        $('.muscle-edit-name').html(muscle_name);
        $('#muscle-edit-edit-link').attr("href", "/exercise/muscle/" + muscle_id + "/edit/");
        $('#muscle-delete-edit-link').attr("href", "/exercise/muscle/" + muscle_id + "/delete/");
    }

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

function weight_log_chart(data, div_id, reps_i18n, width_factor) {

    // Calculate the size
    var width_factor = typeof width_factor !== 'undefined' ? width_factor: 600;
    var height_factor = width_factor / 600 * 200;

    var margin = {top: 20, right: 80, bottom: 30, left: 50},
        width = width_factor - margin.left - margin.right,
        height = height_factor - margin.top - margin.bottom;

    var parseDate = d3.time.format("%Y-%m-%d").parse;

    var x = d3.time.scale()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.category10();

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(6)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .ticks(6)
        .orient("left");

    var line = d3.svg.line()
        .interpolate("cardinal")
        .tension(0.6)
        .x(function (d) { return x(d.date); })
        .y(function (d) { return y(d.weight); });

    var svg = d3.select("#svg-" + div_id).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


      color.domain(d3.keys(data[0]).filter(function (key) {
            return ($.inArray(key, ['date', 'id']) == -1);
    })
        );

      data.forEach(function(d) {
        d.date = parseDate(d.date);
      });


      var reps = color.domain().map(function (name) {

          var temp_values = data.filter(function(d) {
              return (d[name] != 'n.a');
              });

          var filtered_values = temp_values.map(function (d) {
            return {date: d.date,
                    weight: +d[name],
                    log_id: d.id};
            });

        return {
          name: name,
          values: filtered_values
        };
      });

      //console.log(reps);

      x.domain(d3.extent(data, function (d) { return d.date; }));

      // Add 1 kg of "breathing room" on the min value, so the diagrams don't look
      // too flat
      y.domain([
        d3.min(reps, function(c) { return d3.min(c.values, function(v) { return v.weight - 1; }); }),
        d3.max(reps, function(c) { return d3.max(c.values, function(v) { return v.weight; }); })
      ]);

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em");
          //.style("text-anchor", "end")
          //.text("Weight");

      var log_series = svg.selectAll(".log_series")
          .data(reps)
        .enter().append("g")
          .attr("class", "log_series");

      log_series.append("path")
          .attr("class", "line")
          .attr("d", function(d) { return line(d.values); })
          .style("stroke", function(d) { return color(d.name); });

        reps.forEach(function(d){
            var color_name = d.name
            var temp_name = hex_random();
            var color_class = 'color-' + color(color_name).replace('#', '');

            svg.selectAll(".dot" + temp_name)
              .data(d.values)
            .enter().append("circle")
              .attr("class", "dot wger-modal-dialog " + color_class)
              .attr("cx", line.x())
              .attr("cy", line.y())
              .attr("id", function(d) { return d.log_id; })
              .attr("href", function(d) { return '/' + get_current_language() + '/workout/log/edit-entry/' +  d.log_id.match(/\d+/); })
              .attr("r", 5)
              .style("stroke", function(d) {
                return color(color_name);
              });
        });


      log_series.append("text")
          .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
          .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.weight) + ")"; })
          .attr("x", 6)
          .attr("dy", ".35em")
          .text(function(d) { return d.name + " " + reps_i18n; });

    // Make the circles clickable: open their edit dialog
    form_modal_dialog();
}


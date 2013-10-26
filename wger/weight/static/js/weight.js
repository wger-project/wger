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
 * wger weight functions
 */

// Simple helper function that simply returns the y component of an entry
function y_value(d) { return d.y; }

function getDate(d) {
    return new Date(d);
}

function weight_chart(data, width_factor)
{
    // Return if there is no data to process
    if(data == '')
    {
        return;
    }



    // Calculate the size
    var width_factor = typeof width_factor !== 'undefined' ? width_factor: 600;
    var height_factor = width_factor / 600 * 400;
    var height2_factor = width_factor / 600 * 390;
    var bottom_factor = width_factor / 600 * 150;
    var top_factor = width_factor / 600 * 290;

    var minDate = getDate(data[0].x),
        maxDate = getDate(data[data.length-1].x);

    var margin = {top: 10, right: 10, bottom: bottom_factor, left: 40},
        margin2 = {top: top_factor, right: 10, bottom: 50, left: 40},
        width = width_factor - margin.left - margin.right,
        height = height_factor - margin.top - margin.bottom,
        height2 = height2_factor - margin2.top - margin2.bottom;

    var x = d3.time.scale()
        .domain([minDate, maxDate])
        .range([0, width]);
    var x2 = d3.time.scale()
        .domain([minDate, maxDate])
        .range([0, width]);

    var min_y_value = d3.min(data, y_value) - 1;
    var max_y_value = d3.max(data, y_value) + 1;


    var y = d3.scale.linear()
        .domain([min_y_value, max_y_value])
        .range([height, 0]);
    var y2 = d3.scale.linear()
        .domain([min_y_value, max_y_value])
        .range([height2, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(6)
        .orient("bottom");

    var xAxis2 = d3.svg.axis()
        .scale(x2)
        .ticks(6)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var brush = d3.svg.brush()
        .x(x2)
        .on("brush", brush);

    var line = d3.svg.line()
        .x(function(d) { return x(getDate(d.x)); })
        .y(function(d) { return y(d.y); })
        .interpolate('cardinal');

    var line2 = d3.svg.line()
        .x(function(d) { return x2(getDate(d.x)); })
        .y(function(d) { return y2(d.y); })
        .interpolate('cardinal');

    var area = d3.svg.area()
        .x(line.x())
        .y1(line.y())
        .y0(y(min_y_value))
        .interpolate('cardinal');

    var area2 = d3.svg.area()
        .x(line2.x())
        .y1(line2.y())
        .y0(y2(min_y_value))
        .interpolate('cardinal');

    // Reset the content of weight_diagram, otherwise if there is a filter
    // a new SVG will be appended to it
    $("#weight_diagram").html("");

    var svg = d3.select("#weight_diagram").append("svg")
        .datum(data)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    var focus = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var context = svg.append("g")
        .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

    focus.append("path")
        .attr("class", "area")
        .attr("clip-path", "url(#clip)")
        .attr("d", area);

    focus.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    focus.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    focus.append("path")
        .attr("class", "line")
        .attr("clip-path", "url(#clip)")
        .attr("d", line);

    focus.selectAll(".dot")
        .data(data.filter(function(d) { return d.y; }))
      .enter().append("circle")
        .attr("clip-path", "url(#clip)")
        .attr("class", "dot modal-dialog")
        .attr("href", function(d) { return '/' + get_current_language() + '/weight/' + d.id + '/edit/'; })
        .attr("id", function(d) { return d.id; })
        .attr("cx", line.x())
        .attr("cy", line.y())
        .attr("r", 0)
      .transition() // Animate the data points, "opening" them one after another
        .duration(1000)
        .delay(function(d, i) { return i / data.length * 1600; })
        .attr("r", function(d) { return 5; });


    context.append("path")
        .attr("class", "area")
        .attr("d", area2);

    context.append("path")
        .attr("class", "line")
        .attr("d", line2);

    context.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height2 + ")")
      .call(xAxis2);

    context.append("g")
          .attr("class", "x brush")
          .call(brush)
        .selectAll("rect")
          .attr("y", -6)
          .attr("height", height2 + 7);

  function brush() {
      x.domain(brush.empty() ? x2.domain() : brush.extent());
      focus.select("path").attr("d", area);
      focus.select(".line").attr("d", line);

      focus.selectAll(".dot")
          .attr("cx", line.x())
          .attr("cy", line.y());

      focus.select(".x.axis").call(xAxis);
    }

    // Make the circles clickable: open their edit dialog
    form_modal_dialog();
}


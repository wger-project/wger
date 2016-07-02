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
 * wger Nutriton functions
 */

"use strict";

function update_ingredient_value(url)
{
    var form_data = $('#nutritional-values-form').serializeArray();
    $.get(url, form_data, function(data) {

        // Show any validation errors
        $('#calculator-errors').html('');
        if (data['errors'])
        {
            $.each(data['errors'], function(index, value) {
                $('#calculator-errors').append('<p class="ym-message">'+value+'</p>');
            });
        }

        // Replace the nutritional values
        $('#value-energy').html(parseFloat(data['energy']).toFixed(2));
        $('#value-protein').html(parseFloat(data['protein']).toFixed(2));
        $('#value-carbohydrates').html(parseFloat(data['carbohydrates']).toFixed(2));
        $('#value-carbohydrates-sugar').html(parseFloat(data['carbohydrates_sugar']).toFixed(2));
        $('#value-fat').html(parseFloat(data['fat']).toFixed(2));
        $('#value-fat-saturated').html(parseFloat(data['fat_saturated']).toFixed(2));
        $('#value-fibres').html(parseFloat(data['fibres']).toFixed(2));
        $('#value-sodium').html(parseFloat(data['sodium']).toFixed(2));
    });
}

function init_ingredient_detail(url)
{
    // Prevent the form from being sent
    $('#nutritional-values-form').submit(function(e) {
        e.preventDefault();
    });

    $('#id_amount').keyup(function(){
        update_ingredient_value(url);
    });

    $('#id_unit').change(function(){
        update_ingredient_value(url);
    });
}



/*
 * Update the user's preferences
 */
function init_ingredient_autocompleter()
{
    // Init the autocompleter
    $('#id_ingredient_searchfield').devbridgeAutocomplete({
        serviceUrl: '/api/v2/ingredient/search/',
        onSelect: function (suggestion) {
            var ingredient_id = suggestion.data.id;

            // After clicking on a result set the value of the hidden field
            $('#id_ingredient').val(ingredient_id);
            $('#exercise_name').html(suggestion.value);

            // See if the ingredient has any units and set the values for the forms
            $.get('/api/v2/ingredientweightunit/?ingredient=' + ingredient_id, function(unit_data) {

                // Remove any old units, if any
                var options = $('#id_weight_unit').find('option');
                $.each(options, function(index, option_obj) {
                    if (option_obj.value != '')
                    {
                        $(option_obj).remove();
                    }
                });

                // Add new units, if any
                $.each(unit_data.results, function(index, value) {
                    $.get('/api/v2/weightunit/' + value.unit + '/', function(unit) {
                        var unit_name = unit.name + ' (' + value.gram + 'g)';
                        $('#id_unit').append(new Option(unit_name, value.id));
                        $('#id_weight_unit').append(new Option(unit_name, value.id));
                    });
                });
            });
        },
        paramName: 'term',
        transformResult: function(response) {
            // why is response not already a JSON object??
            var jsonResponse = $.parseJSON(response);
            return {
                suggestions: $.map(jsonResponse, function(item) {
                    return {value: item.value, data: {id: item.id}};
                })
            };
        }
    });
}


/*
 * Draw the BMI chart
 */
function render_bmi(width_factor)
{
    // Delete the other diagrams
    d3.selectAll('svg').remove();

    // Calculate the size
    var width_factor = typeof width_factor !== 'undefined' ? width_factor: 600;
    var height_factor = width_factor / 600 * 300;

    var margin = {top: 20, right: 80, bottom: 30, left: 50},
        width = width_factor - margin.left - margin.right,
        height = height_factor - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var z = d3.scale.ordinal().range(['#000080', '#0000ff', '#00ffff', '#00ff00', '#ffff00', '#ff7f2a', '#ff0000', '#800000']);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var stack = d3.layout.stack()
        .offset("zero")
        .values(function(d) { return d.values; })
        .x(function(d) { return d.height; })
        .y(function(d) { return d.weight; });

    var nest = d3.nest()
        .key(function(d) { return d.key; });

    var area = d3.svg.area()
        .interpolate("linear")
        .x(function(d) { return x(d.height); })
        .y0(function(d) { return y(d.y0); })
        .y1(function(d) { return y(d.y); });


    var svg = d3.select("#bmi-chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Clip path, drawings outside are removed
    svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);


    d3.json("/nutrition/calculator/bmi/chart-data", function(data) {

        var layers = stack(nest.entries(data));

        // Manually set the domains
        x.domain([150, 200]); // height, in cm
        y.domain([30, 160]);  // weight, in kg

      svg.selectAll(".layer")
          .data(layers)
        .enter().append("path")
          .attr("class", "layer")
          .attr("id", function(d, i) { return "key-" + d.key; })
          .attr("clip-path", "url(#clip)")
          .attr("d", function(d) { return area(d.values); })
          .style("fill", function(d, i) { return z(i); })
          .style("opacity", 0.6);

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      svg.append("g")
          //.attr("transform", "translate(" + width + ",0)")
          .attr("class", "y axis")
          .call(yAxis);

      var url = $("#bmi-form").attr( 'action' );

        $.post(url,
           $("#bmi-form").serialize(),
           function(data) {
               $('#bmi-result-container').show();
               $('#bmi-result-value').html(data.bmi);
               svg.append("circle")
                .attr("cx", x(data.height))
                .attr("cy", y(data.weight))
                .attr("fill", "black")
                .attr("r", 5);
           });
    });

}


/*
 * Calories calculator
 */
function init_calories_calculator()
{
    $("#form-transfer-calories").click(function(e){
        e.preventDefault();
        var base_calories = Number($('#id_base_calories').html());
        $('#id_calories').val(base_calories);
    });

    $("#add-calories-total").click(function(e){
        e.preventDefault();
        var base_calories = Number($('#id_base_calories').html());
        var additional_calories = Number($('#id_additional_calories').val());
        $('#id_calories').val(base_calories + additional_calories);
    });

    $("#form-update-calories").click(function(e){
        e.preventDefault();

        // Get own ID and update the user profile
        $.get('/api/v2/userprofile', function(data) {
        }).done(function(userprofile) {
            var total_calories = $("#id_calories")[0].value;
            $.ajax({
                url:'/api/v2/userprofile/' + userprofile.results[0].id + '/',
                type: 'PATCH',
                data: {calories: total_calories}
            });
        });
    });

    $(".calories-autoform").click(function(e){
        e.preventDefault();

        // BMR
        var bmr_url = $("#bmr-form").attr('action');
        $.post(bmr_url,
               $("#bmr-form").serialize(),
               function(data) {
                   $('#bmr-result-container').show();
                   $('#bmr-result-value').html(data.bmr);

                   // Activities
                   var activities_url = $("#activities-form").attr('action');
                   $.post(activities_url,
                          $("#activities-form").serialize(),
                          function(data) {
                              $('#activities-result-container').show();
                              $('#activities-result-value').html(data.factor);

                              // Total calories
                              $('#id_base_calories').html(data.activities);
                          });
            });
    });
}

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
 * wger Nutriton functions
 */

'use strict';

function updateIngredientValue(url) {
  var formData = $('#nutritional-values-form').serializeArray();
  $.get(url, formData, function (data) {
    // Show any validation errors
    $('#calculator-errors').html('');
    if (data.errors) {
      $.each(data.errors, function (index, value) {
        $('#calculator-errors').append('<p class="ym-message">' + value + '</p>');
      });
    }

    // Replace the nutritional values
    $('#value-energy').html(parseFloat(data.energy).toFixed(2));
    $('#value-protein').html(parseFloat(data.protein).toFixed(2));
    $('#value-carbohydrates').html(parseFloat(data.carbohydrates).toFixed(2));
    $('#value-carbohydrates-sugar').html(parseFloat(data.carbohydrates_sugar).toFixed(2));
    $('#value-fat').html(parseFloat(data.fat).toFixed(2));
    $('#value-fat-saturated').html(parseFloat(data.fat_saturated).toFixed(2));
    $('#value-fibres').html(parseFloat(data.fibres).toFixed(2));
    $('#value-sodium').html(parseFloat(data.sodium).toFixed(2));
  });
}

function wgerInitIngredientDetail(url) {
  // Prevent the form from being sent
  $('#nutritional-values-form').submit(function (e) {
    e.preventDefault();
  });

  $('#id_amount').keyup(function () {
    updateIngredientValue(url);
  });

  $('#id_unit').change(function () {
    updateIngredientValue(url);
  });
}

/*
 * Update the user's preferences
 */
function wgerInitIngredientAutocompleter() {
  // Init the autocompleter
  $('#id_ingredient_searchfield').autocomplete({
    serviceUrl: '/api/v2/ingredient/search/',
    paramName: 'term',
    minChars: 3,
    onSelect: function (suggestion) {
      var ingredientId = suggestion.data.id;

      // After clicking on a result set the value of the hidden field
      $('#id_ingredient').val(ingredientId);
      $('#exercise_name').html(suggestion.value);

      // See if the ingredient has any units and set the values for the forms
      $.get('/api/v2/ingredientweightunit/?ingredient=' + ingredientId, function (unitData) {
        // Remove any old units, if any
        var options = $('#id_weight_unit').find('option');
        $.each(options, function (index, optionObj) {
          if (optionObj.value !== '') {
            $(optionObj).remove();
          }
        });

        // Add new units, if any
        $.each(unitData.results, function (index, value) {
          $.get('/api/v2/weightunit/' + value.unit + '/', function (unit) {
            var unitName = unit.name + ' (' + value.gram + 'g)';
            $('#id_unit').append(new Option(unitName, value.id));
            $('#id_weight_unit').append(new Option(unitName, value.id));
          });
        });
      });
    }
  });
}

/*
 * Draw the BMI chart
 */
function wgerRenderBodyMassIndex(w) {
  var svg;
  var area;
  var nest;
  var stack;
  var yAxis;
  var xAxis;
  var z;
  var y;
  var x;
  var margin;
  var width;
  var height;
  var heightFactor;
  var widthFactor;

  // Delete the other diagrams
  d3.selectAll('svg').remove();

  // Calculate the size
  if (typeof w === 'undefined') {
    widthFactor = 600;
  } else {
    widthFactor = w;
  }

  heightFactor = (widthFactor / 600) * 300;

  margin = { top: 20, right: 80, bottom: 30, left: 50 };
  width = widthFactor - margin.left - margin.right;
  height = heightFactor - margin.top - margin.bottom;

  x = d3.scaleLinear()
    .range([0, width]);

  y = d3.scaleLinear()
    .range([height, 0]);

  z = d3.scaleOrdinal().range(['#000080',
    '#0000ff',
    '#00ffff',
    '#00ff00',
    '#ffff00',
    '#ff7f2a',
    '#ff0000',
    '#800000']);

  xAxis = d3.axisBottom(x);

  yAxis = d3.axisLeft(y);

  stack = d3.stack();

  nest = d3.nest()
    .key(function (d) {
      return d.key;
    });

  area = d3.area()
    .x(function (d) {
      return x(d.height);
    })
    .y1(function (d) {
      return y(d.weight);
    });

  svg = d3.select('#bmi-chart').append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  // Clip path, drawings outside are removed
  svg.append('defs').append('clipPath')
    .attr('id', 'clip')
    .append('rect')
    .attr('width', width)
    .attr('height', height);

  d3.json('/nutrition/calculator/bmi/chart-data', function (data) {
    var $bmiForm;
    var url;
    var layers;
    stack.keys(['filler',
      'severe_thinness',
      'moderate_thinness',
      'mild_thinness',
      'normal_range',
      'pre_obese',
      'obese_class_2',
      'obese_class_3']);
    layers = stack(nest.entries(data));

    // Manually set the domains
    x.domain(data.map(function (d) {
      return d.height;
    }));
    y.domain([d3.min(data, function (d) {
      return d.weight;
    }), d3.max(data, function (d) {
      return d.weight;
    })]);

    svg.selectAll('.layer')
      .data(layers)
      .enter().append('path')
      .attr('class', 'layer')
      .attr('id', function (d) {
        return 'key-' + d.key;
      })
      .attr('clip-path', 'url(#clip)')
      .attr('d', function (d, i) {
        return area(d[i].data.values);
      })
      .style('fill', function (d, i) {
        return z(i);
      })
      .style('opacity', 1);

    svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(xAxis);

    svg.append('g')
      .attr('class', 'y axis')
      .call(yAxis);

    $bmiForm = $('#bmi-form');
    url = $bmiForm.attr('action');

    $.post(url,
      $bmiForm.serialize(),
      function (postData) {
        $('#bmi-result-container').show();
        $('#bmi-result-value').html(postData.bmi);
        svg.append('circle')
          .attr('cx', x(postData.height))
          .attr('cy', y(postData.weight))
          .attr('fill', 'black')
          .attr('r', 5);
      });
  });
}

/*
 * Calories calculator
 */
function wgerInitCaloriesCalculator() {
  $('#form-transfer-calories').click(function (e) {
    var baseCalories;
    e.preventDefault();
    baseCalories = Number($('#id_base_calories').html());
    $('#id_calories').val(baseCalories);
  });

  $('#add-calories-total').click(function (e) {
    var additionalCalories;
    var baseCalories;
    e.preventDefault();
    baseCalories = Number($('#id_base_calories').html());
    additionalCalories = Number($('#id_additional_calories').val());
    $('#id_calories').val(baseCalories + additionalCalories);
  });

  $('#form-update-calories').click(function (e) {
    e.preventDefault();

    // Get own ID and update the user profile
    $.get('/api/v2/userprofile', function () {
    }).done(function (userprofile) {
      var totalCalories = $('#id_calories')[0].value;
      $.ajax({
        url: '/api/v2/userprofile/' + userprofile.results[0].id + '/',
        type: 'PATCH',
        data: { calories: totalCalories }
      });
    });
  });

  $('.calories-autoform').click(function (e) {
    var $bmrForm;
    var bmrUrl;
    e.preventDefault();

    // BMR
    $bmrForm = $('#bmr-form');
    bmrUrl = $bmrForm.attr('action');
    $.post(bmrUrl,
      $bmrForm.serialize(),
      function (data) {
        var $activitiesForm;
        var activitiesUrl;
        $('#bmr-result-container').show();
        $('#bmr-result-value').html(data.bmr);

        // Activities
        $activitiesForm = $('#activities-form');
        activitiesUrl = $activitiesForm.attr('action');
        $.post(activitiesUrl,
          $activitiesForm.serialize(),
          function (activitiesData) {
            $('#activities-result-container').show();
            $('#activities-result-value').html(activitiesData.factor);

            // Total calories
            $('#id_base_calories').html(activitiesData.activities);
          });
      });
  });
}

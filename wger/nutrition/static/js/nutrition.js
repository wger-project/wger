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
  let formData = $('#nutritional-values-form').serializeArray();
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
    $('#value-energy-kjoule').html(parseFloat(data.energy * 4.184).toFixed(2));
    $('#value-protein').html(parseFloat(data.protein).toFixed(2));
    $('#value-carbohydrates').html(parseFloat(data.carbohydrates).toFixed(2));
    $('#value-carbohydrates-sugar').html(parseFloat(data.carbohydrates_sugar).toFixed(2));
    $('#value-fat').html(parseFloat(data.fat).toFixed(2));
    $('#value-fat-saturated').html(parseFloat(data.fat_saturated).toFixed(2));
    $('#value-fiber').html(parseFloat(data.fiber).toFixed(2));
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
 * Calories calculator
 */
function wgerInitCaloriesCalculator() {
  $('#form-transfer-calories').click(function (e) {
    let baseCalories;
    e.preventDefault();
    baseCalories = Number($('#id_base_calories').html());
    $('#id_calories').val(baseCalories);
  });

  $('#add-calories-total').click(function (e) {
    let additionalCalories;
    let baseCalories;
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
      let totalCalories = $('#id_calories')[0].value;
      $.ajax({
        url: '/api/v2/userprofile/' + userprofile.results[0].user + '/',
        type: 'PATCH',
        data: {calories: totalCalories}
      });
    });
  });

  $('.calories-autoform').click(function (e) {
    let $bmrForm;
    let bmrUrl;
    e.preventDefault();

    // BMR
    $bmrForm = $('#bmr-form');
    bmrUrl = $bmrForm.attr('action');
    $.post(bmrUrl,
      $bmrForm.serialize(),
      function (data) {
        let $activitiesForm;
        let activitiesUrl;
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

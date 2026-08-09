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

function wgerGetCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function updateIngredientValue(url) {
  let form = document.getElementById('nutritional-values-form');
  let params = new URLSearchParams(new FormData(form));

  fetch(url + '?' + params.toString())
    .then((response) => response.json())
    .then(function (data) {
      // Show any validation errors
      let errorContainer = document.getElementById('calculator-errors');
      errorContainer.innerHTML = '';
      if (data.errors) {
        Object.values(data.errors).forEach(function (value) {
          errorContainer.innerHTML += '<p class="ym-message">' + value + '</p>';
        });
      }

      // Replace the nutritional values. Fields without a value (e.g. sugar or
      // sodium) have no element in the page, those are simply skipped.
      let setValue = function (id, value) {
        let element = document.getElementById(id);
        if (element) {
          element.textContent = parseFloat(value).toFixed(2);
        }
      };
      setValue('value-energy', data.energy);
      setValue('value-energy-kjoule', data.energy * 4.184);
      setValue('value-protein', data.protein);
      setValue('value-carbohydrates', data.carbohydrates);
      setValue('value-carbohydrates-sugar', data.carbohydrates_sugar);
      setValue('value-fat', data.fat);
      setValue('value-fat-saturated', data.fat_saturated);
      setValue('value-fiber', data.fiber);
      setValue('value-sodium', data.sodium);
    });
}

function wgerInitIngredientDetail(url) {
  // Prevent the form from being sent
  document.getElementById('nutritional-values-form').addEventListener('submit', function (e) {
    e.preventDefault();
  });

  document.getElementById('id_amount').addEventListener('keyup', function () {
    updateIngredientValue(url);
  });

  document.getElementById('id_unit').addEventListener('change', function () {
    updateIngredientValue(url);
  });
}


/*
 * Calories calculator
 */
function wgerInitCaloriesCalculator() {
  document.getElementById('form-transfer-calories').addEventListener('click', function (e) {
    e.preventDefault();
    let baseCalories = Number(document.getElementById('id_base_calories').textContent);
    document.getElementById('id_calories').value = baseCalories;
  });

  document.getElementById('add-calories-total').addEventListener('click', function (e) {
    e.preventDefault();
    let baseCalories = Number(document.getElementById('id_base_calories').textContent);
    let additionalCalories = Number(document.getElementById('id_additional_calories').value);
    document.getElementById('id_calories').value = baseCalories + additionalCalories;
  });

  document.getElementById('form-update-calories').addEventListener('click', function (e) {
    e.preventDefault();

    // The userprofile endpoint always operates on the current user's profile
    // and updates are done with a POST request, no ID needed
    fetch('/api/v2/userprofile/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': wgerGetCsrfToken()
      },
      body: new URLSearchParams({calories: document.getElementById('id_calories').value})
    });
  });

  document.querySelectorAll('.calories-autoform').forEach(function (form) {
    form.addEventListener('click', function (e) {
      e.preventDefault();

      // BMR
      let bmrForm = document.getElementById('bmr-form');
      fetch(bmrForm.getAttribute('action'), {
        method: 'POST',
        body: new URLSearchParams(new FormData(bmrForm))
      })
        .then((response) => response.json())
        .then(function (data) {
          document.getElementById('bmr-result-container').style.display = '';
          document.getElementById('bmr-result-value').innerHTML = data.bmr;

          // Activities
          let activitiesForm = document.getElementById('activities-form');
          fetch(activitiesForm.getAttribute('action'), {
            method: 'POST',
            body: new URLSearchParams(new FormData(activitiesForm))
          })
            .then((response) => response.json())
            .then(function (activitiesData) {
              document.getElementById('activities-result-container').style.display = '';
              document.getElementById('activities-result-value').innerHTML = activitiesData.factor;

              // Total calories
              document.getElementById('id_base_calories').innerHTML = activitiesData.activities;
            });
        });
    });
  });
}

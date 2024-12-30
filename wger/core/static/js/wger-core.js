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


function getCurrentLanguage() {
  // Returns a short name, like 'en' or 'de'
  return $('#current-language').data('currentLanguage');
}


/*
 Returns a random hex string. This is useful, e.g. to add a unique ID to generated
 HTML elements
 */
function getRandomHex() {
  return Math.floor(
    Math.random() * 0x10000 // 65536

  ).toString(16);
}

/*
 Template-like function that adds form elements to the ajax exercise selection in the edit set page
 */
function addExercise(exercise) {
  let $exerciseSearchLog;
  let resultDiv;
  resultDiv = '<div id="DIV-ID" class="ajax-exercise-select">\n' +
    '  <a href="#" ' +
    'data-role="button" ' +
    'class="btn btn-default btn-xs" ' +
    'style="margin-top: 0.5em;">\n' +
    '    <span class="fa fa-times fa-fw"></span>\n' +
    '    EXERCISE\n' +
    '  </a>\n' +
    '  <input type="hidden" name="exercises" value="EXCERCISE-ID">\n' +
    '</div>';

  // Replace the values into the 'template'
  resultDiv = resultDiv.replace('DIV-ID', getRandomHex());
  resultDiv = resultDiv.replace('EXERCISE', exercise.value);
  resultDiv = resultDiv.replace('EXCERCISE-ID', exercise.id);

  $(resultDiv).appendTo('#exercise-search-log');
  $exerciseSearchLog = $('#exercise-search-log');
  $exerciseSearchLog.scrollTop(0);
  $exerciseSearchLog.trigger('create');
}

function getExerciseFormset(baseId) {
  let formsetUrl;
  let setValue;
  setValue = $('#id_sets').val();
  if (setValue && parseInt(setValue, 10) && baseId && parseInt(baseId, 10)) {
    formsetUrl = '/' + getCurrentLanguage() +
      '/routine/set/get-formset/' + baseId + '/' + setValue;

    $.get(formsetUrl, function (data) {
      let $formsets;
      $formsets = $('#formsets');
      $formsets.append(data);
      $('#exercise-search-log').scrollTop(0);
      $formsets.trigger('create');
    });
  }
}

/*
 Updates all exercise formsets, e.g. when the number of sets changed
 */
function updateAllExerciseFormset() {
  let setValue;
  setValue = $('#id_sets').val();
  if (setValue && parseInt(setValue, 10)) {
    $.each($('#exercise-search-log').find('input'), function (index, value) {
      let promise;
      let exerciseId;
      let formsetUrl;
      exerciseId = value.value;
      promise = $().promise();
      if (exerciseId && parseInt(exerciseId, 10)) {
        formsetUrl = '/' + getCurrentLanguage() +
          '/routine/set/' +
          'get-formset/' + exerciseId + '/' + setValue;
        promise.done(function () {
          promise = $.get(formsetUrl, function (data) {
            let $formsets;
            $('#formset-base-' + exerciseId).remove();
            $formsets = $('#formsets');
            $formsets.append(data);
            $('#exercise-search-log').scrollTop(0);
            $formsets.trigger('create');
          }).promise();
        });
      }
    });
  }
}

/*
 Remove the result DIV (also contains the hidden form element) with the exercise
 formsets when the user clicks on the delete link
 */
function initRemoveExerciseFormset() {
  $('.ajax-exercise-select a').click(function (e) {
    let baseId;
    e.preventDefault();
    baseId = $(this).parent('div').find('input').val();
    $('#formset-base-' + baseId).remove();
    $(this).parent('div').remove();
  });
}

function getSearchLanguages() {
  let search_languages = getCurrentLanguage();
  let search_english = $('#id_english_results')[0].checked;
  if (search_english === true) {
    search_languages = search_languages + ',' + 'en';
  }

  return search_languages;
}

function wgerInitEditSet() {
  // Initialise the autocompleter (our widget, defined above)
  $('#exercise-search').autocomplete({
    serviceUrl: function () {
      return '/api/v2/exercise/search/?language=' + getSearchLanguages()
    },
    showNoSuggestionNotice: true,
    groupBy: 'category',
    paramName: 'term',
    minChars: 3,
    onSelect: function (suggestion) {
      // Add the exercise to the list
      addExercise({
        id: suggestion.data.base_id,
        value: suggestion.value
      });

      // Load formsets
      getExerciseFormset(suggestion.data.base_id);

      // Init the remove buttons
      initRemoveExerciseFormset();

      // Reset the autocompleter
      $(this).val('');
      return false;
    }
  });

  // Mobile select box
  $('#id_exercise_list').change(function () {
    let $idExerciseList;
    let baseId;
    let exerciseName;
    $idExerciseList = $('#id_exercise_list');
    baseId = $idExerciseList.val();
    exerciseName = $idExerciseList.find(':selected').text();
    addExercise({
      id: baseId,
      value: exerciseName
    });
    getExerciseFormset(baseId);
    initRemoveExerciseFormset();
  });

  // Delete button next to exercise
  initRemoveExerciseFormset();

  // Slider to set the number of sets
  $('#id_sets').on('input', function () {
    $('#id_sets_value').html($('#id_sets').val());
  });

  $('#id_sets').on('pointerup', function () {
    updateAllExerciseFormset();
  });

  /*
   * Mobile version only
   */
  // Update the exercise list when the categories change
  $('#id_categories_list').on('change', function () {
    // Remember to filter by exercise language
    $.get('/api/v2/language/?short_name=' + getCurrentLanguage(), function (data) {
      let filter;
      let baseUrl;
      let categoryPk;
      let languagePk;
      languagePk = data.results[0].id;
      categoryPk = $('#id_categories_list').val();
      baseUrl = '/api/v2/exercise/';
      filter = '?limit=999&language=' + languagePk;

      if (categoryPk !== '') {
        filter += '&category=' + categoryPk;
      }

      $.get(baseUrl + filter, function (exerciseData) {
        // Sort the results by name, at the moment it's not possible
        // to search and sort the API at the same time
        let $idExerciseList;
        exerciseData.results.sort(function (a, b) {
          if (a.name < b.name) {
            return -1;
          }
          if (a.name > b.name) {
            return 1;
          }
          return 0;
        });

        // Remove existing options
        $idExerciseList = $('#id_exercise_list');
        $idExerciseList
          .find('option')
          .remove();

        // ..and add the new ones
        $idExerciseList.append(new Option('---------', ''));
        $.each(exerciseData.results, function (index, exercise) {
          $('#id_exercise_list').append(new Option(exercise.name, exercise.id));
        });
      });
    });
  });
}


/*
 Helper function used in the workout log dialog to fetch existing workout sessions through the
 REST API
 */
function wgerGetWorkoutSession() {
  $('#id_date').on('change', function () {
    let date = $('#id_date').val();
    if (date) {
      $.get('/api/v2/workoutsession/?date=' + date, function (data) {
        if (data.results.length === 1) {
          $('#id_notes').val(data.results[0].notes);
          $('#id_impression').val(data.results[0].impression);
          $('#id_time_start').val(data.results[0].time_start);
          $('#id_time_end').val(data.results[0].time_end);
        } else {
          $('#id_notes').val('');
          $('#id_impression').val('2');
          $('#id_time_start').val('');
          $('#id_time_end').val('');
        }
      });
    }
  });
}

$(document).ready(function () {
  // Handle the workout PDF download options for workouts
  $('#download-pdf-button').click(function (e) {
    let targetUrl;
    let token;
    let uid;
    let workoutId;
    let downloadComments;
    let downloadImages;
    let downloadType;
    let downloadInfo;
    e.preventDefault();

    downloadInfo = $('#pdf-download-info');
    downloadType = $('input[name="pdf_type"]:checked').val();
    downloadImages = $('#id_images').is(':checked') ? 1 : 0;
    downloadComments = $('#id_comments').is(':checked') ? 1 : 0;

    workoutId = downloadInfo.data('workoutId');
    uid = downloadInfo.data('uid');
    token = downloadInfo.data('token');

    // Put together and redirect
    targetUrl = '/' + getCurrentLanguage() +
      '/routine/' + workoutId + '/pdf' +
      '/' + downloadType +
      '/' + downloadImages +
      '/' + downloadComments +
      '/' + uid +
      '/' + token;
    window.location.href = targetUrl;
  });

  // Handle the workout PDF download options for schedules
  $('#download-pdf-button-schedule').click(function (e) {
    let targetUrl;
    let token;
    let uid;
    let scheduleId;
    let downloadComments;
    let downloadImages;
    let downloadType;
    let downloadInfo;
    e.preventDefault();

    downloadInfo = $('#pdf-download-info');
    downloadType = $('select[name="pdf_type"]').val();
    downloadImages = $('#id_images').is(':checked') ? 1 : 0;
    downloadComments = $('#id_comments').is(':checked') ? 1 : 0;

    scheduleId = downloadInfo.data('scheduleId');
    uid = downloadInfo.data('uid');
    token = downloadInfo.data('token');

    // Put together and redirect
    targetUrl = '/' + getCurrentLanguage() +
      '/routine/schedule/' + scheduleId + '/pdf' +
      '/' + downloadType +
      '/' + downloadImages +
      '/' + downloadComments +
      '/' + uid +
      '/' + token;
    window.location.href = targetUrl;
  });
});

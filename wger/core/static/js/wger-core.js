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

/*
 AJAX related functions

 See https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax for
 more information
 */
function getCookie(name) {
  var cookie;
  var cookies;
  var cookieValue = null;
  var loopCounter;
  if (document.cookie && document.cookie !== '') {
    cookies = document.cookie.split(';');
    for (loopCounter = 0; loopCounter < cookies.length; loopCounter++) {
      cookie = jQuery.trim(cookies[loopCounter]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // These HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  crossDomain: false, // obviates need for sameOrigin test
  beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type)) {
      xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    }
  }
});

function getCurrentLanguage() {
  // Returns a short name, like 'en' or 'de'
  return $('#current-language').data('currentLanguage');
}

/*
 Setup sortable to make the sets sortable
 */
function wgerSetupSortable() {
  var elements = document.getElementsByTagName('tbody');
  $.each(elements, function (index, element) {
    Sortable.create(element, {
      handle: '.dragndrop-handle',
      animation: 150,
      onUpdate: function (event) {
        var dayId;
        dayId = $(event.target).parents('table').data('id');
        $.each(($(event.from).children('tr')), function (eventIndex, eventElement) {
          var trElement;
          var setId;
          trElement = $(eventElement);

          // The last table element has no ID attribute (has only the 'add exercise' link
          if (trElement.data('id')) {
            setId = trElement.data('id');
            $.ajax({
              url: '/api/v2/set/' + setId + '/',
              type: 'PATCH',
              data: { order: eventIndex + 1 }
            });
          }
        });

        // Replace the content of the table with a fresh version that has
        // correct indexes.
        $.get('/' + getCurrentLanguage() + '/workout/day/' + dayId + '/view/');
        $('#div-day-' + dayId)
          .load('/' + getCurrentLanguage() + '/workout/day/' + dayId + '/view/');
      }
    });
  });
}

/*
 Functions related to the user's preferences
 */


/*
 Updates a single field in the user profile
 */
function setProfileField(field, newValue) {
  var dataDict = {};
  dataDict[field] = newValue;
  $.get('/api/v2/userprofile', function () {
  }).done(function (userprofile) {
    console.log('Updating profile field "' + field + '" to value: ' + newValue);
    $.ajax({
      url: '/api/v2/userprofile/' + userprofile.results[0].id + '/',
      type: 'PATCH',
      data: dataDict
    });
  });
}

/*
 Get a single field from the user's profile.
 Synchronous request, use sparingly!
 */
function getProfileField(field) {
  var result;
  result = null;
  $.ajax({
    url: '/api/v2/userprofile/',
    type: 'GET',
    async: false,
    success: function (userprofile) {
      result = userprofile.results[0][field];
    }
  });
  return result;
}

/*
 Get the current user's username.
 Do not use with anonymous users!
 Synchronous request, use sparingly!
 */
function wgerGetUsername() {
  var userId;
  var result;
  userId = getProfileField('user');
  result = null;
  $.ajax({
    url: '/api/v2/userprofile/' + userId + '/username/',
    type: 'GET',
    async: false,
    success: function (user) {
      result = user.username;
    }
  });
  return result;
}

function wgerToggleComments() {
  $('#exercise-comments-toggle').click(function (e) {
    var showComment;
    e.preventDefault();

    showComment = getProfileField('show_comments');
    if (!showComment) {
      $('.exercise-comments').show();
    } else {
      $('.exercise-comments').hide();
    }

    // Update user profile
    setProfileField('show_comments', !showComment);
  });
}

function wgerToggleReadOnlyAccess() {
  $('#toggle-ro-access').click(function (e) {
    var $shariffModal;
    var roAccess;
    e.preventDefault();
    roAccess = getProfileField('ro_access');

    // Update user profile
    setProfileField('ro_access', !roAccess);

    // Hide and show appropriate divs

    $shariffModal = $('#shariffModal');
    if (!roAccess) {
      $shariffModal.find('.shariff').removeClass('hidden');
      $shariffModal.find('.noRoAccess').addClass('hidden');
    } else {
      $shariffModal.find('.shariff').addClass('hidden');
      $shariffModal.find('.noRoAccess').removeClass('hidden');
    }
  });
}

/*
 Init calls for tinyMCE editor
 */
function wgerInitTinymce() {
  // Only try to init it on pages that loaded its JS file (so they probably need it)
  //
  // See the following links on detail about configuring the menus
  // http://www.tinymce.com/wiki.php/Configuration:toolbar
  // http://www.tinymce.com/wiki.php/Configuration:menu
  if (typeof tinyMCE !== 'undefined') {
    tinyMCE.init({
      // General options
      mode: 'textareas',
      theme: 'modern',
      width: '100%',
      height: '200',
      entity_encoding: 'raw',
      menu: {},
      toolbar: 'undo redo | bold italic | bullist numlist '
    });
  }
}

/*
 Open a modal dialog for form editing
 */
function modalDialogFormEdit() {
  var $submit;
  var $form;
  $form = $('#ajax-info-content').find('form');
  $submit = $($form).find('#form-save');

  $submit.click(function (e) {
    var formData;
    var formAction;
    e.preventDefault();
    formAction = $form.attr('action');
    formData = $form.serialize();

    // Unbind all click elements, so the form doesn't get submitted twice
    // if the user clicks 2 times on the button (while there is already a request
    // happening in the background)
    $submit.off();

    // Show a loader while we fetch the real page
    $form.html('<div style="text-align:center;">' +
      '<img src="/static/images/loader.svg" ' +
      'width="48" ' +
      'height="48"> ' +
      '</div>');
    $('#ajax-info-title').html('Processing'); // TODO: translate this

    // OK, we did the POST, what do we do with the result?
    $.ajax({
      type: 'POST',
      url: formAction,
      data: formData,
      beforeSend: function (jqXHR) {
        // Send a custom header so django's messages are not displayed in the next
        // request which will be not be displayed to the user, but on the next one
        // that will
        jqXHR.setRequestHeader('X-wger-no-messages', '1');
      },
      success: function (data, textStatus, jqXHR) {
        var url = jqXHR.getResponseHeader('X-wger-redirect');
        if (url) {
          window.location.href = url;
          /*
           if(document.URL.indexOf(url)) {
           history.pushState({}, "", url);
           }
           */
        } else if ($(data).find('form .has-error').length > 0) {
          // we must do the same with the new form as before, binding the click-event,
          // checking for errors etc, so it calls itself here again.
          $form.html($(data).find('form').html());
          $('#ajax-info-title').html($(data).find('#page-title').html());
          modalDialogFormEdit();
        } else {
          console.log('No X-wger-redirect found but also no .has-error!');
          $('#wger-ajax-info').modal('hide');
          $form.html(data);
        }

        // Call other custom initialisation functions
        // (e.g. if the form as an autocompleter, it has to be initialised again)
        if (typeof wgerCustomModalInit !== 'undefined') {
          wgerCustomModalInit(); // eslint-disable-line no-undef
        }

        if (typeof wgerCustomPageInit !== 'undefined') {
          wgerCustomPageInit(); // eslint-disable-line no-undef
        }
      },
      error: function (jqXHR) {
        // console.log(errorThrown); // INTERNAL SERVER ERROR
        $('#ajax-info-content').html(jqXHR.responseText);
      }
    });
  });
}

function wgerFormModalDialog() {
  var $wgerModalDialog;
  $wgerModalDialog = $('.wger-modal-dialog');
  // Unbind all other click events so we don't do this more than once
  $wgerModalDialog.off();

  // Load the edit dialog when the user clicks on an edit link
  $wgerModalDialog.click(function (e) {
    var $ajaxInfoContent;
    var targetUrl;
    e.preventDefault();
    targetUrl = $(this).attr('href');

    // It's not possible to have more than one modal open at any time, so close them
    $('.modal').modal('hide');

    // Show a loader while we fetch the real page
    $ajaxInfoContent = $('#ajax-info-content');
    $ajaxInfoContent.html('<div style="text-align:center;">' +
      '<img src="/static/images/loader.svg" ' +
      'width="48" ' +
      'height="48"> ' +
      '</div>');
    $('#ajax-info-title').html('Loading...');
    $('#wger-ajax-info').modal('show');

    $ajaxInfoContent.load(targetUrl + ' .form-horizontal',
      function (responseText, textStatus, XMLHttpRequest) {
        var $ajaxInfoTitle;
        var modalTitle;
        $ajaxInfoTitle = $('#ajax-info-title');
        if (textStatus === 'error') {
          $ajaxInfoTitle.html('Sorry but an error occured');
          $('#ajax-info-content').html(XMLHttpRequest.status + ' ' + XMLHttpRequest.statusText);
        }

        // Call other custom initialisation functions
        // (e.g. if the form as an autocompleter, it has to be initialised again)
        if (typeof wgerCustomModalInit !== 'undefined') {
          // Function is defined in templates. Eslint doesn't check the templates resulting in a
          // un-def error message.
          wgerCustomModalInit(); // eslint-disable-line no-undef
        }

        // Set the new title
        modalTitle = '';
        if ($(responseText).find('#page-title').length > 0) {
          // Complete HTML page
          modalTitle = $(responseText).find('#page-title').html();
        } else {
          // Page fragment
          modalTitle = $(responseText).filter('#page-title').html();
        }
        $ajaxInfoTitle.html(modalTitle);

        // If there is a form in the modal dialog (there usually is) prevent the submit
        // button from submitting it and do it here with an AJAX request. If there
        // are errors (there is an element with the class 'ym-error' in the result)
        // reload the content back into the dialog so the user can correct the entries.
        // If there isn't assume all was saved correctly and load that result into the
        // page's main DIV (#main-content). All this must be done like this because there
        // doesn't seem to be any reliable and easy way to detect redirects with AJAX.
        if ($(responseText).find('.form-horizontal').length > 0) {
          modalDialogFormEdit();
        }
      });
  });
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
  var $exerciseSearchLog;
  var resultDiv;
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

function getExerciseFormset(exerciseId) {
  var formsetUrl;
  var setValue;
  setValue = $('#id_sets').val();
  if (setValue && parseInt(setValue, 10) && exerciseId && parseInt(exerciseId, 10)) {
    formsetUrl = '/' + getCurrentLanguage() +
      '/workout/set/get-formset/' + exerciseId +
      '/' + setValue + '/';

    $.get(formsetUrl, function (data) {
      var $formsets;
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
  var setValue;
  setValue = $('#id_sets').val();
  if (setValue && parseInt(setValue, 10)) {
    $.each($('#exercise-search-log').find('input'), function (index, value) {
      var promise;
      var exerciseId;
      var formsetUrl;
      exerciseId = value.value;
      promise = $().promise();
      if (exerciseId && parseInt(exerciseId, 10)) {
        formsetUrl = '/' + getCurrentLanguage() +
          '/workout/set/get-formset/' + exerciseId +
          '/' + setValue + '/';
        promise.done(function () {
          promise = $.get(formsetUrl, function (data) {
            var $formsets;
            $('#formset-exercise-' + exerciseId).remove();
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
    var exerciseId;
    e.preventDefault();
    exerciseId = $(this).parent('div').find('input').val();
    $('#formset-exercise-' + exerciseId).remove();
    $(this).parent('div').remove();
  });
}

function wgerInitEditSet() {
  // Initialise the autocompleter (our widget, defined above)
  $('#exercise-search').autocomplete({
    serviceUrl: '/api/v2/exercise/search/?language=' + getCurrentLanguage(),
    showNoSuggestionNotice: true,
    groupBy: 'category',
    paramName: 'term',
    minChars: 3,
    onSelect: function (suggestion) {
      // Add the exercise to the list
      addExercise({
        id: suggestion.data.id,
        value: suggestion.value
      });

      // Load formsets
      getExerciseFormset(suggestion.data.id);

      // Init the remove buttons
      initRemoveExerciseFormset();

      // Reset the autocompleter
      $(this).val('');
      return false;
    }
  });

  // Mobile select box
  $('#id_exercise_list').change(function () {
    var $idExerciseList;
    var exerciseId;
    var exerciseName;
    $idExerciseList = $('#id_exercise_list');
    exerciseId = $idExerciseList.val();
    exerciseName = $idExerciseList.find(':selected').text();
    addExercise({
      id: exerciseId,
      value: exerciseName
    });
    getExerciseFormset(exerciseId);
    initRemoveExerciseFormset();
  });

  // Delete button next to exercise
  initRemoveExerciseFormset();

  // Slider to set the number of sets
  $('#id_sets').on('change', function () {
    updateAllExerciseFormset();
    $('#id_sets_value').html($('#id_sets').val());
  });

  /*
   * Mobile version only
   */
  // Update the exercise list when the categories change
  $('#id_categories_list').on('change', function () {
    // Remember to filter by exercise language
    $.get('/api/v2/language/?short_name=' + getCurrentLanguage(), function (data) {
      var filter;
      var baseUrl;
      var categoryPk;
      var languagePk;
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
        var $idExerciseList;
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
 Helper function to load the target of a link into the main-content DIV (the main left colum)
 */
function wgerLoadMaincontent() {
  $('.load-maincontent').click(function (e) {
    var targetUrl;
    e.preventDefault();
    targetUrl = $(this).attr('href');

    $.get(targetUrl, function (data) {
      var currentUrl;
      // Load the data
      $('#main-content').html($(data).find('#main-content').html());

      // Update the browser's history
      currentUrl = $(data).find('#current-url').data('currentUrl');
      history.pushState({}, '', currentUrl);

      wgerLoadMaincontent();
    });
  });
}

/*
 Helper function to prefetch images on a page
 */
function wgerPrefetchImages(imageArray) {
  $(imageArray).each(function () {
    (new Image()).src = this;
    // console.log('Preloading image' + this);
  });
}

/*
 Helper function used in the workout log dialog to fetch existing workout sessions through the
 REST API
 */
function wgerGetWorkoutSession() {
  $('#id_date').on('change', function () {
    var date = $('#id_date').val();
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
    var targetUrl;
    var token;
    var uid;
    var workoutId;
    var downloadComments;
    var downloadImages;
    var downloadType;
    var downloadInfo;
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
      '/workout/' + workoutId + '/pdf' +
      '/' + downloadType +
      '/' + downloadImages +
      '/' + downloadComments +
      '/' + uid +
      '/' + token;
    window.location.href = targetUrl;
  });

  // Handle the workout PDF download options for schedules
  $('#download-pdf-button-schedule').click(function (e) {
    var targetUrl;
    var token;
    var uid;
    var scheduleId;
    var downloadComments;
    var downloadImages;
    var downloadType;
    var downloadInfo;
    e.preventDefault();

    downloadInfo = $('#pdf-download-info');
    downloadType = $('input[name="pdf_type"]:checked').val();
    downloadImages = $('#id_images').is(':checked') ? 1 : 0;
    downloadComments = $('#id_comments').is(':checked') ? 1 : 0;

    scheduleId = downloadInfo.data('scheduleId');
    uid = downloadInfo.data('uid');
    token = downloadInfo.data('token');

    // Put together and redirect
    targetUrl = '/' + getCurrentLanguage() +
      '/workout/schedule/' + scheduleId + '/pdf' +
      '/' + downloadType +
      '/' + downloadImages +
      '/' + downloadComments +
      '/' + uid +
      '/' + token;
    window.location.href = targetUrl;
  });
});

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

/*jslint browser: true*/
/*global $, jQuery, alert*/


/*
 * Own functions
 *
 */

"use strict";

function get_current_language() {
    /* Returns a short name, like 'en' or 'de' */
    return $('#current-language').data('currentLanguage');
}

/*
 * Define an own widget, which is basically an autocompleter that groups
 * results by category
 */
$.widget("custom.catcomplete", $.ui.autocomplete, {
    _renderMenu: function (ul, items) {
        var that = this,
            currentCategory = "";
        $.each(items, function (index, item) {
            if (item.category !== currentCategory) {

                ul.append("<li class='ui-autocomplete-category'>" + item.category + "</li>");
                currentCategory = item.category;
            }
            that._renderItemData(ul, item);
        });
    },
    _renderItem: function (ul, item) {
        var li_style = '';
        if (item.image) {
            li_style = "style='background-image:url(" + item.image_thumbnail + ");background-size:30px 30px;background-repeat:no-repeat;'";
        }

        return $("<li " + li_style + ">")
            .append("<a style='margin-left:30px;'>" + item.name + "</a>")
            .appendTo(ul);
    }
});


/*
 * Setup JQuery sortables to make the sets sortable
 */
function setup_sortable() {
    $(".workout-table tbody").sortable({
        handle: '.dragndrop-handle',
        revert: true,
        update : function (event, ui) {
            // Monkey around the HTML, till we find the IDs of the set and the day
            var day_element = ui.item.parent().parent().find('tr').first().attr('id'); //day-xy
            var day_id = day_element.match(/\d+/);

            // returns something in the form "set-1,set-2,set-3,"
            var order = $(this).sortable('toArray');

            //$("#ajax-info").show();
            //$("#ajax-info").addClass('success');
            $.get('/' + get_current_language() + "/workout/api/edit-set" + "?do=set_order&day_id=" + day_id + "&order=" + order);


            // TODO: it seems to be necessary to call the view two times before it returns
            //       current data.
            $.get('/' + get_current_language() + "/workout/day/" + day_id + "/view/");
            $("#div-day-" + day_id).load('/' + get_current_language() + "/workout/day/" + day_id + "/view/");
        }
    });
}


/*
 *
 * Functions related to the user's preferences
 *
 */
function toggle_comments() {
    $("#exercise-comments-toggle").click(function (e) {
        e.preventDefault();

        if (showComment === 0) {
            $('.exercise-comments').show();
            showComment = 1;
        } else if (showComment === 1) {
            $('.exercise-comments').hide();
            showComment = 0;
        }

        $("#ajax-info").load('/' + get_current_language() + "/workout/api/user-preferences?do=set_show-comments&show=" + showComment);
    });
}



/*
 * Init calls for tinyMCE editor
 */
function init_tinymce() {

    // Only try to init it on pages that loaded its JS file (so they probably need it)
    //
    // See the following links on detail about configuring the menus
    // http://www.tinymce.com/wiki.php/Configuration:toolbar
    // http://www.tinymce.com/wiki.php/Configuration:menu
    if (typeof tinyMCE !== 'undefined') {
        tinyMCE.init({
            // General options
            mode : "textareas",
            theme : "modern",
            width : "100%",
            height : "200",
            entity_encoding : "raw",
            menu: {},
            toolbar: "undo redo | bold italic | bullist numlist "
        });
    }
}


/*
 * Open a modal dialog for form editing
 */
function form_modal_dialog() {
    // Unbind all other click events so we don't do this more than once
    $(".wger-modal-dialog").off();

    // Load the edit dialog when the user clicks on an edit link
    $(".wger-modal-dialog").click(function (e) {
        e.preventDefault();
        var targetUrl = $(this).attr("href");

        // Show a loader while we fetch the real page
        $("#ajax-info-content").html('<div style="text-align:center;">' +
                                '<img src="/static/images/loader.svg" ' +
                                     'width="48" ' +
                                     'height="48"> ' +
                             '</div>');
        //$("#wger-ajax-info").modal({title: 'Loading...'});
        $("#wger-ajax-info").modal("show");

        $("#ajax-info-content").load(targetUrl + " .form-horizontal",
                                     function(responseText, textStatus, XMLHttpRequest){
                                        // Call other custom initialisation functions
                                        // (e.g. if the form as an autocompleter, it has to be initialised again)
                                        if (typeof custom_modal_init !== "undefined") {
                                            custom_modal_init();
                                        }

                                        // Set the new title
                                        $("#ajax-info-title").html($(responseText).find("#page-title").html());

                                        // If there is a form in the modal dialog (there usually is) prevent the submit
                                        // button from submitting it and do it here with an AJAX request. If there
                                        // are errors (there is an element with the class 'ym-error' in the result)
                                        // reload the content back into the dialog so the user can correct the entries.
                                        // If there isn't assume all was saved correctly and load that result into the
                                        // page's main DIV (#main-content). All this must be done like this because there
                                        // doesn't seem to be any reliable and easy way to detect redirects with AJAX.
                                        if ($(responseText).find(".form-horizontal").length > 0) {
                                            modal_dialog_form_edit();
                                        }
                                     });
    });
}


function modal_dialog_form_edit() {
    var form = $("#ajax-info-content").find("form");
    var submit = $(form).find("#form-save");

    submit.click(function (e) {
        e.preventDefault();
        var form_action = form.attr('action');
        var form_data = form.serialize();

        // Unbind all click elements, so the form doesn't get submitted twice
        // if the user clicks 2 times on the button (while there is already a request
        // happening in the background)
        submit.off();

        // Show a loader while we fetch the real page
        $("#ajax-info-content form").html('<div style="text-align:center;">' +
                                '<img src="/static/images/loader.svg" ' +
                                     'width="48" ' +
                                     'height="48"> ' +
                             '</div>');
        $("#ajax-info-title").html('Processing'); // TODO: translate this


        // OK, we did the POST, what do we do with the result?
        $.ajax({
            type: "POST",
            url: form_action,
            data: form_data,
            beforeSend: function (jqXHR, settings) {
                // Send a custom header so django's messages are not displayed in the next
                // request which will be not be displayed to the user, but on the next one
                // that will
                jqXHR.setRequestHeader("X-wger-no-messages", "1");
            },
            success: function (data,  textStatus, jqXHR) {
                if ($(data).find('form .has-error').length > 0) {
                    // we must do the same with the new form as before, binding the click-event,
                    // checking for errors etc, so it calls itself here again.
                    $("#ajax-info-content form").html($(data).find('form').html());
                    $("#ajax-info-title").html($(data).find("#page-title").html());
                    modal_dialog_form_edit();
                } else {
                    $("#wger-ajax-info").modal("hide");

                    // If there  was a redirect we must change the URL of the browser. Otherwise
                    // a reload would not change the adress bar, but the content would.
                    // Since it is not possible to get this URL from the AJAX request, we read it out
                    // from a hidden HTML DIV in the document...
                    var current_url = $(data).find("#current-url").data('currentUrl');

                    // TODO: There seems to be problems sometimes when using the technique below and
                    //       bootstrap's menu bar (drop downs won't open). So just do a normal
                    //       redirect.
                    window.location.href = current_url;


                    /*
                    if(document.URL.indexOf(current_url))
                    {
                        history.pushState({}, "", current_url);
                    }
                    */

                    // Note: loading the new page like this executes all its JS code
                    //$('body').html(data);
                }

                // Call other custom initialisation functions
                // (e.g. if the form as an autocompleter, it has to be initialised again)
                if (typeof custom_modal_init !== "undefined") {
                    custom_modal_init();
                }

                if (typeof custom_page_init !== "undefined") {
                    custom_page_init();
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //console.log(errorThrown); // INTERNAL SERVER ERROR
                $("#ajax-info-content").html(jqXHR.responseText);
            }
        });
    });

}



/*
 * Returns a random hex string. This is useful, e.g. to add a unique ID to generated
 * HTML elements
 */
function hex_random() {
    return Math.floor(
        Math.random() * 0x10000 /* 65536 */
    ).toString(16);
}


/*
 * Template-like function that adds form elements to the ajax exercise selection
 * in the edit set page
 */
function add_exercise(exercise) {
    var result_div = '<div id="DIV-ID" class="ajax-exercise-select"> \
<a href="#" data-role="button" class="btn btn-default btn-xs"> \
<img src="/static/images/icons/status-off.svg" \
     width="14" \
     height="14" \
     alt="Delete"> \
EXERCISE \
</a> \
<input type="hidden" name="exercises" value="EXCERCISE-ID"> \
</div>';

    // Replace the values into the 'template'
    result_div = result_div.replace('DIV-ID', hex_random());
    result_div = result_div.replace('EXERCISE', exercise.value);
    result_div = result_div.replace('EXCERCISE-ID', exercise.id);

    $(result_div).prependTo("#exercise-search-log");
    $("#exercise-search-log").scrollTop(0);
    $('#exercise-search-log').trigger('create');
}

function get_exercise_formset(exercise_id) {
    var set_value = $('#id_sets').val();
    if (set_value && parseInt(set_value, 10) && exercise_id && parseInt(exercise_id, 10)) {
        var formset_url = '/' + get_current_language() +
                          '/workout/get-formset/' +  exercise_id +
                          '/' + set_value + '/';

        $.get(formset_url, function (data) {
            $('#formsets').prepend(data);
            $("#exercise-search-log").scrollTop(0);
            $('#formsets').trigger("create");
        });
    }
}

// Updates all exercise formsets, e.g. when the number of sets changed
function update_all_exercise_formset() {
    var set_value = $('#id_sets').val();
    if (set_value && parseInt(set_value, 10)) {
        $.each($('#exercise-search-log input'), function (index, value) {

            var exercise_id = value.value;
            if (exercise_id && parseInt(exercise_id, 10)) {
                var formset_url = '/' + get_current_language() +
                            '/workout/get-formset/' +  exercise_id +
                            '/' + set_value + '/';
                $.get(formset_url, function (data) {
                    $('#formset-exercise-' + exercise_id).remove();
                    $('#formsets').prepend(data);
                    $('#exercise-search-log').scrollTop(0);
                    $('#formsets').trigger("create");
                });
            }
        });
    }
}

/*
 * Remove the result DIV (also contains the hidden form element) with the exercise
 * formsets when the user clicks on the delete link
 */
function init_remove_exercise_formset() {
    $(".ajax-exercise-select a").click(function (e) {
        e.preventDefault();
        var exercise_id = $(this).parent('div').find('input').val();
        $('#formset-exercise-' + exercise_id).remove();
        $(this).parent('div').remove();
    });
}

function init_edit_set() {
    // Initialise the autocompleter (our widget, defined above)
    $("#exercise-search").catcomplete({
        source: '/' + get_current_language() + "/exercise/search/",
        minLength: 2,
        select: function (event, ui) {

            // Add the exercise to the list
            add_exercise(ui.item);

            // Load formsets
            get_exercise_formset(ui.item.id);

            // Init the remove buttons
            init_remove_exercise_formset();

            // Reset the autocompleter
            $(this).val("");
            return false;
        }
    });

    // Mobile select box
    $('#id_exercise_list').change(function (e) {
        var exercise_id = $('#id_exercise_list').val();
        var exercise_name = $('#id_exercise_list').find(":selected").text();
        add_exercise({id: exercise_id,
                      value: exercise_name});
        get_exercise_formset(exercise_id);
        init_remove_exercise_formset();
    });

    // Delete button next to exercise
    init_remove_exercise_formset();

    // Slider to set the number of sets
    $("#slider").slider({
        range: "min",
        value: $("#id_sets").val(),
        step: 1,
        min: 1,
        max: 7,
        slide: function (event, ui) {
            $("#id_sets").val(ui.value);
            $("#slider-show").html(ui.value);
            update_all_exercise_formset();
        }
    });
}

function init_schedule_datepicker() {
    $("#id_start_date").datepicker();
}

function init_weight_datepicker() {
    $("#id_creation_date").datepicker();
}

function init_weight_log_datepicker() {
    $("#id_date").datepicker();
}



function toggle_weight_log_table() {
    $(".weight-chart-table-toggle").click(function (e) {
        e.preventDefault();
        var target = $(this).data('toggleTarget');
        $('#' + target).toggle({effect: 'blind', duration: 600});
    });
}

/*
 *
 * Helper function to load the target of a link into the main-content DIV (the
 * main left colum)
 *
 */
function load_maincontent() {
    $(".load-maincontent").click(function (e) {
        e.preventDefault();
        var targetUrl = $(this).attr("href");

        $.get(targetUrl, function (data) {
            // Load the data
            $('#main-content').html($(data).find('#main-content').html());

            // Update the browser's history
            var current_url = $(data).find("#current-url").data('currentUrl');
            history.pushState({}, "", current_url);

            load_maincontent();
        });
    });
}

/*
 * Helper function to prefetch images on a page
 */
function prefetch_images(imageArray) {
    $(imageArray).each(function () {
        (new Image()).src = this;
        //console.log('Preloading image' + this);
    });
}


/*
 * Helper function used in the workout log dialog to fetch existing
 * workout sessions through the REST API
 */
 function get_workout_session() {
    $('#id_date').on('change', function() {
        var date = $('#id_date').val();
        if(date) {
            $.get( '/api/v1/workoutsession/?date=' + date, function( result ) {
                if (result.objects.length == 1) {
                    $('#id_notes').val(result.objects[0].notes)
                    $('#id_impression').val(result.objects[0].impression)
                    $('#id_time_start').val(result.objects[0].time_start)
                    $('#id_time_end').val(result.objects[0].time_end)
                }
                else {
                    $('#id_notes').val('');
                    $('#id_impression').val('2');
                    $('#id_time_start').val('');
                    $('#id_time_end').val('');
                }
            });
        }
    });
}
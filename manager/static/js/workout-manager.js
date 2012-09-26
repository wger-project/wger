/* 
 * Own functions 
 * 
 */


/*
 * Setup JQuery sortables to make the sets sortable
 */
function setup_sortable()
{
    // Hide the edit options for the set, this is done with the in-place editing
    $(".set-options").hide();

    $(".workout-table tbody").sortable({
        handle: '.dragndrop-handle',
        revert: true,
        update : function (event, ui) {
                // Monkey around the HTML, till we find the IDs of the set and the day
                var day_element = ui.item.parent().parent().find('tr').first().attr('id'); //day-xy
                var day_id = day_element.match(/\d+/);
                
                // returns something in the form "set-1,set-2,set-3,"
                var order = $( this ).sortable('toArray');

                //$("#ajax-info").show();
                //$("#ajax-info").addClass('success');
                $.get("/workout/api/edit-set" + "?do=set_order&day_id=" + day_id + "&order=" + order)
                
                
                // TODO: it seems to be necessary to call the view two times before it returns
                //       current data.
                $.get("/workout/day/view/" + day_id);
                $("#div-day-" + day_id).load("/workout/day/view/" + day_id);
        }
        
    })
    
    // Allow the settings within an exercise to be sortable
    $(".settings-list").sortable({
        placeholder: 'sortable-settings',
        revert: true,
        tolerance: 'pointer',
        helper: function(event, ui) {
            //return ui;
            return $('<div class="sortable-settings-drag">' + ui.html() + '</div>');
        },
        update : function (event, ui) {
            // returns something in the form "setting-1,setting-2,setting-3,"
            var order = $( this ).sortable('toArray');
        
            // Load the day-ID
            var day_element = ui.item.parents('table').find('tr').attr('id'); //day-xy
            var day_id = day_element.match(/\d+/);

            //$("#ajax-info").show();
            //$("#ajax-info").addClass('success');
            $("#ajax-info").load("/workout/api/edit-settting?do=set_order&order=" + order);
            
            // TODO: it seems to be necessary to call the view two times before it returns
            //       current data.
            $.get("/workout/day/view/" + day_id);
            $("#div-day-" + day_id).load("/workout/day/view/" + day_id);
        }
    });
}


/*
 * Setup JQuery calls to edit the sets
 */
function setup_ajax_set_edit()
{
    // Unbind all other click events so we don't do this more than once
    $(".ajax-set-edit").off();
    
    $(".ajax-set-edit").click(function(e) {
        e.preventDefault();
        
        var set_element = $(this).parents('tr').attr('id');
        var set_id = set_element.match(/\d+/);
        
        var exercise_id = $(this).parents('li').attr('id').match(/\d+/);
        
        
        $($(this).parents('li')).load("/workout/api/edit-set?do=edit_set&set=" + set_id + "&exercise=" + exercise_id);
    });
}

/*
 * 
 * Functions related to the user's preferences
 * 
 */
function toggle_comments()
{
    $("#exercise-comments-toggle").click(function(e) {
        e.preventDefault();
        
        
        if ( showComment == 0 )
        {
            $('.exercise-comments').show();
            showComment = 1;
        }
        else if ( showComment == 1 )
        {
            $('.exercise-comments').hide();
            showComment = 0;
        }
        
        $("#ajax-info").load("/workout/api/user-preferences?do=set_show-comments&show=" + showComment);
    });
}

function set_english_ingredients()
{
    $("#ajax-english-ingredients").click(function(e) {
        e.preventDefault();
        
        
        if ( useEnglishIngredients == 0 )
        {
            $('#english-ingredients-status').attr("src", "/static/images/icons/status-on.svg");
            useEnglishIngredients = 1;
        }
        else if ( useEnglishIngredients == 1 )
        {
             $('#english-ingredients-status').attr("src", "/static/images/icons/status-off.svg");
             useEnglishIngredients = 0;
        }
        
        $("#ajax-info").load("/workout/api/user-preferences?do=set_english-ingredients&show=" + useEnglishIngredients);
    });
}


function setup_inplace_editing()
{
    $(".ajax-form-cancel").each(function(index, element) {
        
        
        var exercise_id = $(this).parents('li').attr('id').match(/\d+/);
        var day_id = $(this).parents('table').attr('id').match(/\d+/);
        var set_id = $(this).parents('tr').attr('id').match(/\d+/);
        
        // Editing of set
        $(element).click(function(e) {
            e.preventDefault();
            $("#div-day-" + day_id).load("/workout/day/view/" + day_id);
        })
        
        // Send the Form
        $('.ajax-form-set-edit').submit(function(e) {
          e.preventDefault();
          
          url = "/workout/api/edit-set?do=edit_set&set=" + set_id + "&exercise=" + exercise_id
          form_data = $(this).serialize();
          $.post( url, form_data);
          
          $("#div-day-" + day_id).load("/workout/day/view/" + day_id);
        });
        
        // Init the autocompleter
        $(".ajax-form-exercise-list").autocomplete({
                source: "/exercise/search/",
                minLength: 2,
                select: function(event, ui) {
    
                    // After clicking on a result set the value of the hidden field
                    $('#set-' + set_id + '-exercercise-id-hidden').val(ui.item.id);
                }
            });
    });
}


/*
 * Init calls for tinyMCE editor
 */
function init_tinymce () {
    
    // Only try to init it on pages that loaded its JS file (so they probably need it)
    if (typeof tinyMCE != 'undefined')
    {
        tinyMCE.init({
            // General options
            mode : "textareas",
            theme : "simple",
            width : "100%",
            height : "200"
        });
   }
}


/*
 * Open a modal dialog for editing
 */
function form_modal_dialog()
{
    // Initialise a modal dialog
    $("#ajax-info").dialog({
                autoOpen: false,
                width: 600,
                modal: true,
                position: 'top'
    });

    // Unbind all other click events so we don't do this more than once
    $(".modal-dialog").off();

    // Load the edit dialog when the user clicks on an edit link
    $(".modal-dialog").click(function(e) {
        e.preventDefault();
        var targetUrl = $(this).attr("href");

        $("#ajax-info").load(targetUrl + " .ym-form", function() {
            // Initialise the WYSIWYG editor
            init_tinymce();
            
            // Call other custom initialisation functions
            // (e.g. if the form as an autocompleter, it has to be initialised again)
            if (typeof custom_modal_init != "undefined")
            {
                custom_modal_init();
            }
        
            // Open the dialog
            $("#ajax-info").dialog("open");
        });
    });
}

function scatterplot_modal_dialog(id)
{
        var targetUrl = '/weight/add/' + id
        
        $("#ajax-info").load(targetUrl + " .ym-form", function() {
            // Open the dialog
            $("#ajax-info").dialog("open");
        });
}

function init_ingredient_autocompleter()
{
    // Init the autocompleter
    $("#id_ingredient_searchfield").autocomplete({
        source: "/nutrition/ingredient/search/",
        minLength: 2,
        select: function(event, ui) {
            
            // After clicking on a result set the value of the hidden field
            $('#id_ingredient').val(ui.item.id);
        }
    });
}


/*
 * Returns a random hex string. This is useful, e.g. to add a unique ID to generated
 * HTML elements
 */
function hex_random()
{
    return Math.floor(
        Math.random() * 0x10000 /* 65536 */
    ).toString(16);
}


/*
 * Template-like function that adds form elements to the ajax exercise selection
 * in the edit set page
 */
function add_exercise(exercise)
{
    var result_div = '<div id="DIV-ID" class="ajax-exercise-select"> \
<a href="#"> \
<img src="/static/images/icons/status-off.svg" \
     width="14" \
     height="14" \
     alt="Delete"> \
</a> EXERCISE \
<input type="hidden" name="exercises" value="EXCERCISE-ID"> \
</div>';
    
    // Replace the values into the 'template'
    result_div = result_div.replace('DIV-ID', hex_random());
    result_div = result_div.replace('EXERCISE', exercise.value);
    result_div = result_div.replace('EXCERCISE-ID', exercise.id); 
    
    $(result_div).prependTo("#exercise-search-log");
    $("#exercise-search-log").scrollTop(0);
}



function init_edit_set()
{
    // Validate the form with JQuery
    $(".ym-form").validate({
                    rules: {
                        sets: {
                            required: true,
                            number: true,
                            max: 6
                        }
                    }
                    
                    });

    // The multi-select exercise list is not needed if javascript is activated
    $('#form-exercises').remove();
    
    // Initialise the autocompleter
    $("#exercise-search").autocomplete({
            source: "/exercise/search/",
            minLength: 2,
            select: function(event, ui) {

                // Add the exercise to the list
                add_exercise(ui.item);
                
                // Remove the result div (also contains the hidden form element) when the user
                // clicks on the delete link
                $(".ajax-exercise-select a").click(function(e) {
                    e.preventDefault();
                    $(this).parent('div').remove();
                });
            }
        });
}

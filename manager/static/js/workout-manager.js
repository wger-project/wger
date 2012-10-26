/* 
 * Own functions 
 * 
 */


/*
 * Define an own widget, which is basically an autocompleter that groups
 * results by category
 */
$.widget( "custom.catcomplete", $.ui.autocomplete, {
        _renderMenu: function( ul, items ) {
            var that = this,
                currentCategory = "";
            $.each( items, function( index, item ) {
                if ( item.category != currentCategory ) {
                    ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
                    currentCategory = item.category;
                }
                that._renderItemData( ul, item );
            });
        }
    });


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
        
        var set_id = $(this).parents('tr').attr('id').match(/\d+/);
        var exercise_id = $(this).parents('.ajax-set-edit-target').attr('id').match(/\d+/);
        
        load_edit_set($(this).parents('.ajax-set-edit-target'), set_id, exercise_id)
    });
}

function load_edit_set(element, set_id, exercise_id)
{
    $(element).load("/workout/api/edit-set?do=edit_set&set=" + set_id + "&exercise=" + exercise_id);
}

function setup_inplace_editing()
{
    $(".ajax-form-cancel").each(function(index, element) {
        
        
        var exercise_id = $(this).parents('.ajax-set-edit-target').attr('id').match(/\d+/);
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
        $(".ajax-form-exercise-list").catcomplete({
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

        // Show a loader while we fetch the real page
        $("#ajax-info").html('<div style="text-align:center;">'+
                                '<img src="/static/images/loader.svg" ' +
                                     'width="48" ' +
                                     'height="48"> ' +
                             '</div>');
        $("#ajax-info").dialog({title: 'Loading...'});
        $("#ajax-info").dialog("open");
        
        $("#ajax-info").load(targetUrl + " .ym-form", function(responseText, textStatus) {
            // Call other custom initialisation functions
            // (e.g. if the form as an autocompleter, it has to be initialised again)
            if (typeof custom_modal_init != "undefined")
            {
                custom_modal_init();
            }
        
            // Set its title and open the dialog
            $("#ajax-info").dialog({title: $(responseText).find("#main-content h2").html()});
            //$("#ajax-info").dialog("open");
        });
    });
}


function scatterplot_modal_dialog(id)
{
        var targetUrl = '/weight/' + id + '/edit/'
        
        $("#ajax-info").load(targetUrl + " .ym-form", function() {
            // Open the dialog
            $("#ajax-info").dialog("open");
            
            // Initialise the datepicker for the modal dialog
            init_weight_datepicker();
        });
        
        
}

function init_ingredient_autocompleter()
{
    // Init the autocompleter
    $("#id_ingredient_searchfield").catcomplete({
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
                    errorClass:'form-error',
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
    
    // Initialise the autocompleter (our widget, defined above)
    $("#exercise-search").catcomplete({
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
                
                // Reset the autocompleter
                $(this).val("");
                return false;
            }
        });
}

function init_weight_datepicker()
{
    $( "#id_creation_date" ).datepicker({ dateFormat: "yy-mm-dd" });
}



/*
 * 
 * D3js functions
 * 
 */
// Simple helper function that simply returns the y component of an entry
function y_value(d) { return d.y; }

function getDate(d) {
    return new Date(d);
}

function weight_chart(data)
{
    // Return if there is no data to process
    if(data == '')
    {
        return;
    }
    
    var minDate = getDate(data[0].x),
        maxDate = getDate(data[data.length-1].x);
    
    var margin = {top: 10, right: 10, bottom: 20, left: 40},
        width = 600 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;
    
    var x = d3.time.scale()
        .domain([minDate, maxDate])
        .range([0, width]);
    
    var min_y_value = d3.min(data, y_value) - 1;
    var max_y_value = d3.max(data, y_value) + 1;
    
    
    var y = d3.scale.linear()
        .domain([min_y_value, max_y_value])
        .range([height, 0]);
    
    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(6)
        .orient("bottom");
        
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");
    
    var line = d3.svg.line()
        .x(function(d) { return x(getDate(d.x)); })
        .y(function(d) { return y(d.y); });
    
    var area = d3.svg.area()
        .x(line.x())
        .y1(line.y())
        .y0(y(min_y_value));
    
    // Reset the content of weight_diagram, otherwise if there is a filter
    // a new SVG will be appended to it
    $("#weight_diagram").html("");
    
    var svg = d3.select("#weight_diagram").append("svg")
        .datum(data)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    
    svg.append("path")
        .attr("class", "area")
        .attr("d", area);
    
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
    
    svg.append("path")
        .attr("class", "line")
        .attr("d", line);
    
    svg.selectAll(".dot")
        .data(data.filter(function(d) { return d.y; }))
      .enter().append("circle")
        .attr("class", "dot")
        .attr("id", function(d) { return d.id; })
        .attr("cx", line.x())
        .attr("cy", line.y())
        .attr("r", 5);
    
    
    // Make the circles clickable: open their edit dialog
    $('circle').click(function(e) {
            entry_id = $(this).attr('id').match(/\d+/);
            scatterplot_modal_dialog(entry_id);
        });
}

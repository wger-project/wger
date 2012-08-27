/* 
 * Own functions 
 * 
 */


/*
 * Setup JQuery sortables to make the sets sortable
 */
function setup_sortable()
{
    $(".workout-table tbody").sortable({
        handle: 'td.ym-g10',
        revert: true,
        update : function (event, ui) {
                // Monkey around the HTML, till we find the IDs of the set and the day
                day_element = ui.item.parent().parent().find('tr').first().attr('id'); //day-xy
                day_id = day_element.match(/\d+/);
                
                // returns something in the form "set-1,set-2,set-3,"
                order = $( this ).sortable('toArray');

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
			order = $( this ).sortable('toArray');
			
			// Load the day-ID
            day_element = ui.item.parents('table').find('tr').attr('id'); //day-xy
            day_id = day_element.match(/\d+/);
			
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
	$(".ajax-set-edit").click(function(e) {
	    e.preventDefault();
	    
	    set_element = $(this).parents('tr').attr('id');
	    set_id = set_element.match(/\d+/);
	    
	    exercise_id = $(this).parents('li').attr('id').match(/\d+/);
	    
	    
	    $($(this).parents('li')).load("/workout/api/edit-set?do=edit_set&set=" + set_id + "&exercise=" + exercise_id);
	});
}

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

function setup_inplace_editing()
{
	$(".ajax-form-cancel").each(function(index, element) {
		
		
		exercise_id = $(this).parents('li').attr('id').match(/\d+/);
		day_id = $(this).parents('table').attr('id').match(/\d+/);
		set_id = $(this).parents('tr').attr('id').match(/\d+/);
		
		// Editing of set
		$(element).click(function(e) {
		    e.preventDefault();
	    	$("#div-day-" + day_id).load("/workout/day/view/" + day_id);
	 	})
	 	
	 	// Send the Form
	 	$(element).submit(function(e) {
		  e.preventDefault();
		  
		  url = "/workout/api/edit-set?do=edit_set&set=" + set_id + "&exercise=" + exercise_id
		  form_data = $(this).serialize();
		  $.post( url, form_data);
		  
		  $("#div-day-" + day_id).load("/workout/day/view/" + day_id);
        });
		
		// Init the autocompleter
	    $(element).autocomplete({
	            source: "/exercise/search/",
	            minLength: 2,
	            select: function(event, ui) {
	
	                // After clicking on a result set the value of the hidden field
	                $('#set-' + set_id + '-exercercise-id-hidden').val(ui.item.id);
	            }
	        });
	});
}
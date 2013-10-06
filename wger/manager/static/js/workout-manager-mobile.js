/*
 *
 *
 * Custom JS code for the mobile version
 *
 *
 */



/*
 * There are no datepickers in the mobile version
 */
function init_weight_datepicker()
{
}

/*
 * Open a modal dialog for form editing
 */
function form_modal_dialog()
{
    // Unbind all other click events so we don't do this more than once
    $(".modal-dialog").off();

    // Load the edit dialog when the user clicks on an edit link
    $(".modal-dialog").click(function(e) {
        e.preventDefault();
        window.location.href = $(this).attr("href");
    });
}


/*
 * Handle external links with a Web Activity when in Firefox OS
 */
$(document).on('pageinit', function () {
    if(typeof MozActivity != 'undefined') {
        /*
         * External links
         */
        $('a[href^=http]').click(function(e){
            e.preventDefault();

            var activity = new MozActivity({
                name: "view",
                data: {
                  type: "url",
                  url: $(this).attr("href")
                }
            });
        });
    }
    else {
        console.debug('MozActivity not available, opening links as usual.');
    }
});

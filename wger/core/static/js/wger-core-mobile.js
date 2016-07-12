/*
 *
 *
 * Custom JS code for the mobile version
 *
 *
 */
"use strict";


/*
 * Handle external links with a Web Activity when in Firefox OS
 */
$(document).ready(function() {
    if (typeof MozActivity != 'undefined') {
        /*
         * External links
         */
        $('a[href^=http]').click(function (e) {
            e.preventDefault();

            var activity = new MozActivity({
                name: "view",
                data: {
                    type: "url",
                    url: $(this).attr("href")
                }
            });
        });
    } else {
        console.debug('MozActivity not available, opening links as usual.');
    }
});
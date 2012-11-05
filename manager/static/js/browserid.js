/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($) {
    'use strict';

    $(function() {
        var requestOptions = [
            'siteName',
            'siteLogo',
            'oncancel',
            'privacyPolicy',
            'returnTo',
            'termsOfService'
        ];

        $(document).delegate('.browserid-login, #browserid', 'click', function(e) {
            e.preventDefault();

            // Arguments to navigator.id.request can be specified by data-attributes
            // on the BrowserID link: <a href="#" data-site-name="Site Name">
            var options = {};
            var $link = $(e.target);
            for (var k = 0; k < requestOptions.length; k++) {
                var name = requestOptions[k];
                var value = $link.data(name);
                if (value !== undefined) {
                    options[name] = value;
                }
            }

            navigator.id.request(options); // Triggers BrowserID login dialog.
        });

        $('.browserid-logout').bind('click', function(e) {
            e.preventDefault();
            navigator.id.logout(); // Clears User Agent BrowserID state.
        });

        navigator.id.watch({
            onlogin: function(assertion) {
                if (assertion) {
                    var $e = $('#id_assertion');
                    $e.val(assertion.toString());
                    $e.parent().submit();
                }
            },

            onlogout: function() {
                // TODO: Detect if logout button was a link and follow its href
                // if possible.
            }
        });
    });
})(jQuery);

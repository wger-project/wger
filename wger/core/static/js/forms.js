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
 * Disables the submit buttons of forms marked with `data-disable-on-submit`
 * once they are submitted, so a double click cannot send the same request
 * twice.
 *
 * The buttons are disabled even when another script cancels the submit event:
 * the reCAPTCHA v3 widget intercepts the event to fetch a token first and then
 * submits the form programmatically, which does not fire a second event.
 */

document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.hasAttribute('data-disable-on-submit')) {
        return;
    }
    form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((button) => {
        button.disabled = true;
    });
});

// Browsers restore the page from the back-forward cache with the buttons still
// disabled, so re-enable them when the page is shown again
window.addEventListener('pageshow', (event) => {
    if (!event.persisted) {
        return;
    }
    document
        .querySelectorAll('form[data-disable-on-submit] [type="submit"]')
        .forEach((button) => {
            button.disabled = false;
        });
});

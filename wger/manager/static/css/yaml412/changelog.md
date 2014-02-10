# Version 4.1.2  (13-07-28)
This is the second maintenance release for YAML 4.1.x path. Thanks to Alexander Haß and MDMueller for their contributions.

## Bug Fixes
### Forms Module
* added support for input[type="image"] elements to forms module (issue #28)
* rearranged form styles for RTL support to avoid specificity conflicts
* corrected several small problems in RTL mode in forms module, especially in columnar view. (issue #30)

### Navigation Module
* removed round corners of search field in hlist navigation on iOS (issue #31)

## Code Changes
### Forms Module
* added "clear:both" for .ym-message class to avoid conflicts when messages are placed behind the form field in the markup. (issue #35)

### Sass
* several improvements were made to the gradient generator, including a fallback for oldIE browsers.

# Version 4.1.1  (13-06-27)
This is the first maintenance release for YAML 4.1.x path

## General
* added RTL support for form theme: gray-theme.css

## Bug Fixes
### Normalization Module
* removed &lt;hgroup&gt; element from normalization module (removed from the HTML5 specs)

### Forms Module
* fixed a wrong margins between .ym-fbox siblings - #6
* fixed missing button adjustments in form linearization - #9
* fixed button style for search button in hlist navigation on iOS - #10
* fixed a problem with .ym-inline elements in columnar mode, issue #20
* fixed a problem with .ym-message in columnar mode, issue #21

### Navigation Module
* fixed border for navigation title in vlist - #8

### Misc
* fixed several typos in CSS comments
* deleted some irrelevant styles from rtl-files - #15

## Code Changes
### Forms Module
* added new custom button class .ym-reply - #7
* added rtl-support for forms: yaml/add-ons/rtl-support/forms/gray-theme-rtl.css - #11, #12

### Add-ons
* reduced file size of microformats icons and base64 inline images

### Demos
* unified HTML structure for the seach field in RTL demo: rtl-support.html #16

# Version 4.1.0 (13-06-11)
A big thanks goes to the following contributors for their help on this version:

  * Jens Grochtdreis (@flocke)
  * Michael Schulze (@michsch)
  * Frederic Hemberger (@fhemberger)

## General
* Moved development from private SVN to public Github repository
* Switched development code base from static CSS to Sass + Compass.
* YAML can now be used as static CSS framework (as in the past) or as a highly configurable Sass/Compass module.
* Added Grunt support to create custom YAML builds, including namespace configuration

## Code Changes
### Normalization Module
* added &lt;main&gt; element to normalization module
* added overflow correction for &lt;svg&gt; elements in IE 9
* added h[x]:target rules to remove outline in Webkit browsers

### Column Module
* fixed a bug where responsive images were always scaled to full size by adding `table-layout:fixed` to column wrapper

### Forms Module
* simplified markup: type classes `.ym-fbox-[text|select|check|button]` are now optional and only needed for IE 6 support.
* form elements now use `box-sizing:border-box` as default in all browsers down to IE 8.
* reduced specificity for form elements to allow easier override styles.
* changed standard width of form elements to 70%. Now element widths are equal in default and columnar view mode.
* added class `.ym-fbox` for styling form rows.
* added class `.ym-fbox-footer` as special form row, intended as a footer that holds all buttons.
* added class `.ym-fbox-wrap` as a wrapper to align multiple form elements in a row.
* added class `.ym-inline` to enable the usage of individual inline form elements.
* added custom button types (primary, positive, warning, danger)
* added custom button sizes (xlarge, large, small, xsmall)
* added 3 new custom buttons (close, sign, support)

### Typography Module
* Changed the margin direction for vertical rhythm from `margin-top` to `margin-bottom`

### Print Module
* removed forced linearization for grids and columns module for print media

### Add-ons
* Accessible Tabs jQuery plugin
 * Update to version 1.9.7  (jQuery 1.9.x support)
 * tabs.css - added print styles to enable printing of tabbed content
* SyncHeight jQuery plugin
  * Update to version 1.5 (jQuery 1.9.x support)
* Microformats
  * added Base64 encoded inline images to reduce HTTP requests in modern browsers, fallback for old IE's included

### Demos
* Updated all layout demos to use the HTML5 &lt;main&gt; element

### Other Changes
* added HTML5shiv to project and updated all references in HTML files
* updated jQuery to v1.10.1 and added jQuery Migration Plugin v1.2.1 to project

# Version 4.0.2
## Bug Fixes
* tabs.css: fixed a float-dropping bug of generated tabs in Chrome 22
* vlist-rtl.css: fixed a bug where first level selectors didn't overwrite ltr-settings
* docs: Fixed a IE 7 rendering-bug in column configuration snippet "2cols - sidebar left"
* docs: Added an info-message about the behavior of responsive media elements in environments wrapped with display:table
* gray-theme.css: bugfix for missing icons in custom buttons on HTC devices with Android 2.2

# Version 4.0.1

## Bug Fixes
* base.css: added two missing commas in CSS selectors
* microformats.css: removed shorthand value from backround-image property
* typography.css: added height:auto to .flexible to avoid scaling problems
* docs: fixed positioning in deeplink navigation
* docs: corrected several typos
* vlist.css: fixed a selector (missing namespace)
* typography.css: removed double-defined selector "pre"

## Improvements
* extended documentation for column module (code snippets for 2-column scenarios)
* grid linearization now works in combination with .ym-equalize
* added progressive linearization feature for forms (by forcing "full" style)
* added documentation for classes .ym-error, .ym-message, .ym-required, .ym-label and .ym-noprint
* changed default markup of vlist navigation (its now similar to hlist navigation)
* updated Accessible Tabs Plugin to v1.9.4

# Version 4.0
YAML 4 brings a lot of changes and improvements, starting with a completely rewritten documentation, improved framework features and new set of layout demos.
## Changes
### A new documentation
YAMLs new documentation comes as an offline-capable HTML file. It provides a lot of useful code snippets, ready to use them via copy & paste in your project. We will try to improve the docs in the future based on your feedback.

### Namespaces
All core features of the CSS framework are namespaced with the prefix "ym-". This helps to avoid conflicts with third party CSS code - a common problem especially in bigger projects.

### Bulletproof flexible grid module
YAML was one of the first framework projects that implemented a flexible grid system. Over 6 years of constant development on the framework the flexible grid module has proven its crossbrowser stability. In YAML 4 it becomes easily customizeable. Now you can design with YAMLs default fluid grid as well as fixed-width custom grid. And it offers you an easy solution for progressive linearization.

### Flexible forms with themeing support
Since version 3.2 YAML offers a form toolkit for flexible forms. This toolkit has been greatly improved by separating functional styles (located in the framework's core style sheet) and theme-stylesheets for the visual form design. As a developer you can build on this toolkit to create even complex forms in a simple way. You can create new, reusable form themes - which helps to makes prototyping and modifications of forms less complicated.

### Matched building blocks
YAML offers several different layout modules, such as grids, columns, navigation bars, form elements, typography, etc. All default styles are matched to each other in order to provide a clean gray-scaled base for rapid prototyping.

# Version 3.3.1
## Bug Fixes
* Bugfix:  yaml-focusfix.js - fixed a small bug in classname detection
* Bugfix:  base.css & base-rtl.css - skiplink CSS produced a huge horizontal scrollbar in FF4
* Bugfix:  markup.html - corrected wrong filename to include "yaml-focusfix.js"
* Update:  Updated jQuery Library to current stable release 1.6.1
* Update:  Updated "Accessible Tabs" add-on to current stable release 1.9.1

# Version 3.3

## Improvements & Feature Changes in YAML-Core
* New: base.css - Support for HTML5 Elements: set block-model to allow structural formatting(article, aside, canvas, details, figcaption, figure, footer, header, hgroup, menu, nav, section, summary)
* Improvement:  base.css - removed last remaining positioning properties for #nav, #main, #header and #topnav from base.css
* Improvement:  base.css - changed containing floats solution for .floatbox to contain floats without clipping: display:table; width: 100%;
* Improvement:  base.css - changed containing floats solution for subtemplates to: display:table; width: 100%;
* Improvement:  base.css - moved non-general parts of the italics fix to iehacks.css to save some bytes in modern browsers.
* Improvement:  iehacks.css - trigger hasLayout for subcolumns content boxes in print layout (containing floats).
* Improvement:  yaml-focusfix.js - rewritten JS code (thanks to Mathias 'molily' Schäfer for contribution)

## Improvements & Feature Changes in YAML
* Improvement:  forms.css - changed clearing for form rows (.type-text etc.) and fieldsets to clearfix to ease CSS3 form styling
* Improvement:  content_default.css - new default values for &lt;sub&gt; and &lt;sup&gt;

## General Changes
* Improvment: removed @charset rule from all stylesheets to avoid problems with several CSS minimizer tools.

# Version 3.2.1
## Improvements & Feature Changes in YAML-Core
* Renamed:      yaml-focusfix.js - The JS file webkit-focusfix.js (introduced in v3.2) was renamed due to the extended support for more browsers
* Improvement:  iehacks.css - simplified Clearfix adjustments for IE 5.x - 7.0
* Improvement:  yaml-focusfix.js - no more pollution of global namespace
* Improvement:  yaml-focusfix.js - added IE8 support and fallback solution for older webkit browsers

## Improvements & Feature Changes in YAML
* Improvement:  content_default.css - better contrast on a:focus {} (keyboard acessibility)
* Improvement:  yaml/navigation: all navigation stylesheets  - adjusted :focus() styles to avoid overruling
* Improvement:  forms.css - improved robustness for "columnar" and "full" form layout (avoiding float drops)
* Improvement:  forms.css - included fix for IE7 auto-padding bug when using buttons

## Changes in Examples
* Improvement:  equal_height_boxes.html - better accessibility for complex example (hidden more links within content boxes)
* Bugfix:       flexible_grids2.html - added new skiplink styling to its basemod_grids2.css
* Bugfix:       equal_height_boxes.html - added new skiplink styling to its basemod_equal_heights.css


# Version 3.2

## Improvements & Feature Changes in YAML-Core
* New:          base.css - merged base.css and print_base.css (smaller filesize)
* New:          base.css - New subtemplate-set (20%, 40%, 60% and 80%), equalized mode is available
* New:          base.css - new skip link solution, that allows overlaying
* New:          js/webkit-focusfix.js - JavaScript based fix for focus problems in Webkit-browsers (Safari, Google Chrome)
* Improvement:  base.css - Split up media types to "all", "screen & projection" and "print", helped to avoid several problems in print layout.
* Improvement:  base.css - using child selectors for equalize-definitions saved about 400 bytes of code
* Improvement:  base.css - moved visual print settings (fontsize & hidden containers) to print-stylesheets
* Improvement:  iehacks.css - improved code for robustness of all major layout elements
* Bugfix:       base.css - removed &lt;dfn&gt; from the hidden elements again
* Bugfix:       iehacks.css - fixed a bug that made subtemplates invisible in IE 5.01
* Bugfix:       slim_iehacks.css - Clearfix hack was broken in IE7
* Feature Drop: base.css - removed code to force vertical scrollbars in FF, Safari & Opera (replaced by CSS3 solution in user files)
* Feature Drop: iehacks.css - removed compatibility code for #page_margins and #page IDs.
* Feature Drop: iehacks.css - column backgrounds using #col3's border-definition aren't available anymore, due to accessibility and maintenance issues in IE
* Improvement:  slightly better optimized slim-versions of core-files.

## Improvements & Feature Changes in YAML
* New:          forms.css - added .full class as an option to get full width &lt;input&gt;, &lt;select&gt; and &lt;textarea&gt; elements within e.g. subcolumns
* New:          content_default.css - added styles for &lt;big&gt;, &lt;small&gt;, &lt;dfn&gt; and &lt;tt&gt;

* Improvement:  forms.css - .yform class can be added to any element. It's not bundled with form-element anymore.
* Improvement:  forms.css - ajdusted fieldset- & div-paddings to avoid clipping of element outlines and dropshadows in Safari.
* Improvement:  forms.css - cleaner and easier fix for fieldset/legend problem in all IE's (including IE8).
* Improvement:  forms.css - Formatting for "reset" and "submit" buttons changed from IDs to classes to allow multiple forms on a webpage. Styling available via input[type=reset] or input.reset to older support IE versions (IE5.x & IE6).
* Improvement:  content_default.css - added a fix to &lt;sub&gt;, &lt;sub&gt; to prevent the visual increase of line-height.
* Improvement:  nav_slidingdoor.css - Removed predefined indent margin of 50px. Indention has to be set by the user in basemod.css
* Improvement:  nav_shinybuttons.css - Removed predefined indent padding of 50px. Indention has to be set by the user in basemod.css

* Bugfix:       forms.css - corrected issue in Firefox 1.x & 2.x where form labels weren't shown correctly in columnar display (FF-Bug)
* Bugfix:       forms.css - no more jumping checkboxes & radiobuttons in IE8 and Opera
* Bugfix:       basemod_draft.css - changed predefined selectors #page_margins and #page into .page_margins and .page
* Bugfix:       content_default.css - nested lists (ol,ul) will be displayed correctly now.
* Bugfix:       markup_draft.html - moved charset metatag in front of title element to allow UTF-8 there

* Feature Drop: debug.css - removed debug-stylesheet from yaml/ folder. This feature is replaced by the new YAML Debug Application (http://debug.yaml.de)

* Update:       tools/dreamweaver_7/base.css - updated to recent codebase.
* Update:       updated jQuery library to version 1.3.2

## Improvement & Feature Changes in YAML-Add-ons
* New Add-on:   Accessible-Tabs plugin for jQuery
* New Add-on:   SyncHeight plugin for jQuery

* Improvement:  Microformats - added missing icons: xfn-child.png, xfn-parent.png, xfn-small.png and xfn-spouse.png
* Improvement:  RTL-Support - iehacks-rtl.css: added an option to force the vertical scrollbar to the right in Internet Explorer (disabled by default)

## Changes in Examples
* New Feature:  All examples - added WAI-ARIA landmark roles for accessibility improvement
* New Feature:  All examples - added optional CSS3-based code to force vertical scrollbars (overflow-y)
* New Example:  multicolumnar_forms.html - demonstrates two easy ways to create flexible multicolumnar forms
* New Example:  accessible_tabs.html - example for the usage of the Accessible-Tabs and the SyncHeight add-on
* New Example:  3col_liquid_faux_columns.html - demonstrates "Liquid Faux Columns" technique
* Improvement:  3col_gfxborder.html - changed ID's to classes to allow multiple usage
* Improvement:  building_forms.html - JavaScript Detection added
* Improvement:  equal_height_boxes.html - added a second usage example (simple)
* Improvement:  dynamic_layout_switching.html - added JavaScript detection code
* Improvement:  dynamic_layout_switching.html - added "show all columns" option
* Removed:      3col_column_backgrounds.html - this feature isn't supported anymore due to accessibility issues
* Bugfix:       2col_right_13.html - corrected fix for 3-pixel-bug in IE-patch file
* Bugfix:       dynamic_layout_switching.html - corrected fix for 3-pixel-bug in IE-patch file
* Bugfix:       equal_height_boxes.html - still used #page_margins and #page ID's.
* Bugfix:       index.html - link to last example corrected
* Bugfix:       several CSS files were still not saved in UTF-8
* Bugfix:       UTF-8 BOM signature removed from some files in examples/04_layout_styling/

# Version 3.1
## General Changes
* markup changes: ID's #page_margins and #page are changed into classes for multiple usage within a single layout
* navigation elements: changed ID's to classes for easier usage, changed classnames for consistency
* forms support included
* better standard content styling
* example section rearanged
* added a small navigation to cycle through all examples
* new example "styling_content" included
* new example "building_forms" included
* new example "flexible grids II" included
* new example "fullpage 3col" included
* new example "fullpage grids" included
* new example "equal_height_boxes" included
* new example "dynamic_layout_switching" included
* add-on: "right to left" language support included
* add-on: microformats support included

## Core-Files
### base.css
* added bugfix for FF rendering of select element
* added properties for blockquote and q element to reset block
* added .equalize class for "equal heights" support
* .skip, .hide, .print ... removed property "width & height: 1px" to allow bringing content back on screen more easy
* added dfn element to the hidden elements

### iehacks.css
* added patches for class .equalize ("equal heights" support)
* added class .no-ie-padding to enable bottom positioning in IE
* changed z-index fix, so that content in #col3 can be selected again in IE 5.x | 6.0

### print_base.css
* removed font changes for print (unit change to "pt" remains as Gecko-Fix)
* rearanged user draft print-stylesheets
* added class .noprint

### other Bug Fixes
* nav_shiny_buttons: collapsing horizontal margins fixed

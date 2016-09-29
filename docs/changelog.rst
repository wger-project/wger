Changelog
=========

1.8 - IN DEVELOPMENT
--------------------
**2016-XX-XX**

Upgrade steps from 1.7:

* Django update to 1.9: ``pip install -r requirements.txt``
* Database upgrade: ``python manage.py migrate``
* Reset cache: ``python manage.py clear-cache --clear-all``
* Due to changes in the JS package management, you have to delete
  wger/core/static/bower_components and do a ``python manage.py bower install``
* Update static files (only production): ``python manage.py collectstatic``
* Load new the languages fixtures as well as their configuration
  ``python manage.py loaddata languages`` and
  ``python manage.py loaddata language_config``
* New config option in settings.py: ``WGER_SETTINGS['TWITTER']``. Set this if
  your instance has its own twitter account.

New languages:

* Norwegian (many thanks to Kjetil Elde `@w00p`_ `#304`_)

New features:

* Add repetition (minutes, kilometer, etc.) and weight options (kg, lb, plates, until failure) to sets `#216`_ and `#217`_
* Allow administrators to deactivate the guest user account `#330`_
* Exercise names are now capitalized, making them more consistent `#232`_
* Much improved landing page (thanks `@DeveloperMal`_) `#307`_
* Add extended PDF options to schedules as well (thanks `@alelevinas`_ ) `#272`_
* Show trained secondary muscles in workout view (thanks `@alokhan`_ ) `#282`_
* Use the metricsgraphics library to more easily draw charts `#188`_
* Removed persona (browserID) as a login option, the service is being discontinued `#331`_

Improvements:

* Check and enforce style guide for JS files `#317`_ (`@petervanderdoes`_)
* BMI calculator now works with pounds as well (thanks `@petervanderdoes`_) `#318`_
* Give feedback when autocompleter didn't find any results `#293`_
* Better GUI consistency in modal dialogs (thanks `@jstoebel`_ ) `#274`_
* Fields in workout log form are no longer required, making it possible to only log weight for certain exercises `#334`_
* The dashboard page was improved and made more user friendly `#201`_ (partly)
* Replace jquery UI's autocompleter and sortable this reduces size of JS and CSS `#78`_ and `#79`_
* Update to D3js v4 `#314`_, `#302`_
* Remove hard-coded CC licence from documentation and website `#247`_

Other improvements and bugfixes:     `#25`_, `#243`_, `#279`_, `#275`_, `#270`_,
`#258`_, `#257`_, `#263`_, `#269`_, `#296`_, `#297`_, `#303`_, `#311`_, `#312`_,
`#313`_, `#322`_, `#324`_, `#325`_


.. _#25: https://github.com/wger-project/wger/issues/25
.. _#78: https://github.com/wger-project/wger/issues/78
.. _#79: https://github.com/wger-project/wger/issues/79
.. _#188: https://github.com/wger-project/wger/issues/188
.. _#201: https://github.com/wger-project/wger/issues/201
.. _#216: https://github.com/wger-project/wger/issues/216
.. _#217: https://github.com/wger-project/wger/issues/217
.. _#232: https://github.com/wger-project/wger/issues/232
.. _#243: https://github.com/wger-project/wger/issues/243
.. _#247: https://github.com/wger-project/wger/issues/247
.. _#263: https://github.com/wger-project/wger/issues/263
.. _#269: https://github.com/wger-project/wger/issues/269
.. _#272: https://github.com/wger-project/wger/issues/272
.. _#274: https://github.com/wger-project/wger/issues/274
.. _#282: https://github.com/wger-project/wger/issues/282
.. _#293: https://github.com/wger-project/wger/issues/293
.. _#296: https://github.com/wger-project/wger/issues/296
.. _#297: https://github.com/wger-project/wger/issues/297
.. _#302: https://github.com/wger-project/wger/issues/302
.. _#303: https://github.com/wger-project/wger/issues/303
.. _#304: https://github.com/wger-project/wger/issues/304
.. _#307: https://github.com/wger-project/wger/issues/307
.. _#311: https://github.com/wger-project/wger/issues/311
.. _#312: https://github.com/wger-project/wger/issues/312
.. _#313: https://github.com/wger-project/wger/issues/313
.. _#314: https://github.com/wger-project/wger/issues/314
.. _#317: https://github.com/wger-project/wger/issues/317
.. _#318: https://github.com/wger-project/wger/issues/318
.. _#322: https://github.com/wger-project/wger/issues/322
.. _#324: https://github.com/wger-project/wger/issues/324
.. _#325: https://github.com/wger-project/wger/issues/325
.. _#330: https://github.com/wger-project/wger/issues/330
.. _#331: https://github.com/wger-project/wger/issues/331
.. _#334: https://github.com/wger-project/wger/issues/334
.. _@petervanderdoes: https://github.com/petervanderdoes
.. _@DeveloperMal: https://github.com/DeveloperMal
.. _@alelevinas: https://github.com/alelevinas
.. _@jstoebel: https://github.com/jstoebel
.. _@alokhan: https://github.com/alokhan
.. _@w00p: https://github.com/w00p



1.7
---
**2016-02-28**

New translations:

* Czech (many thanks to Tomáš Z.!)
* Swedish (many thanks to ywecur!)


New features:

* Workout PDF can now print the exercises' images and comments `#261`_
* Allow login with username or email (thanks `@warchildmd`_) #164`_
* Correctly use user weight when calculating nutrional plans' calories (thanks `@r-hughes`_) `#210`_
* Fix problem with datepicker `#192`_
* Order of exercises in supersets is not reverted anymore `#229`_
* Improvements to the gym management:

  * Allow to add contracts to members
  * Visual consistency for lists and actions
  * Vastly reduce the number of database queries in gym member list `#144`_
  * Global list of users for installation `#212`_
  * Allow administrators to restrict user registration `#220`_
  * Refactored and improved code, among others `#208`_
  * Allow gym managers to reset a member's password `#186`_

* Better rendering of some form elements `#244`_
* Improved GUI consistency `#149`_
* Docker images for easier installation `#181`_
* Use hostname for submitted exercises (thanks `@jamessimas`_) `#159`_
* Download js libraries with bowerjs (thanks `@tranbenny`_) `#126`_
* Improved and more flexible management commands `#184`_
* Fixed error when importin weight entries from CSV (thanks `@r-hughes`_) `#204`_
* Fixed problems when building and installing the application on Windows (thanks `@romansp`_) `#197`_
* Fixed potential Denial Of Service attack (thanks `@r-hughes`_) `#238`_
* Dummy data generator can not create nutrition plans (thanks `@cthare`_) `#241`_


Other improvements and bugfixes: `#279`_, `#275`_, `#270`_, `#258`_, `#257`_


.. _#126: https://github.com/wger-project/wger/issues/126
.. _#144: https://github.com/wger-project/wger/issues/144
.. _#149: https://github.com/wger-project/wger/issues/149
.. _#159: https://github.com/wger-project/wger/issues/159
.. _#164: https://github.com/wger-project/wger/issues/164
.. _#181: https://github.com/wger-project/wger/issues/181
.. _#184: https://github.com/wger-project/wger/issues/184
.. _#186: https://github.com/wger-project/wger/issues/186
.. _#192: https://github.com/wger-project/wger/issues/192
.. _#197: https://github.com/wger-project/wger/issues/197
.. _#204: https://github.com/wger-project/wger/issues/204
.. _#208: https://github.com/wger-project/wger/issues/208
.. _#210: https://github.com/wger-project/wger/issues/210
.. _#212: https://github.com/wger-project/wger/issues/212
.. _#229: https://github.com/wger-project/wger/issues/229
.. _#220: https://github.com/wger-project/wger/issues/220
.. _#238: https://github.com/wger-project/wger/issues/238
.. _#241: https://github.com/wger-project/wger/issues/241
.. _#244: https://github.com/wger-project/wger/issues/244
.. _#257: https://github.com/wger-project/wger/issues/257
.. _#258: https://github.com/wger-project/wger/issues/258
.. _#261: https://github.com/wger-project/wger/issues/261
.. _#270: https://github.com/wger-project/wger/issues/270
.. _#275: https://github.com/wger-project/wger/issues/275
.. _#279: https://github.com/wger-project/wger/issues/279
.. _@jamessimas: https://github.com/jamessimas
.. _@r-hughes: https://github.com/r-hughes
.. _@romansp: https://github.com/romansp
.. _@cthare: https://github.com/cthare
.. _@warchildmd: https://github.com/warchildmd
.. _@tranbenny: https://github.com/tranbenny


1.6.1
-----
**2015-07-25**

Bugfix release


1.6
---
**2015-07-25**

New translations:

* Greek (many thanks to Mark Nicolaou!)

New features:

* Save planed weight along with the repetitions `#119`_
* Improvements to the workout calendar `#98`_
* Allow external access to workouts and other pages to allow for sharing `#102`_, `#124`_
* Email reminder to regularly enter (body) weight entries `#115`_
* Allow users to submit corrections to exercises
* Add day detail view in workout calendar `#103`_
* Fix bug where the exercises added to a superset did not remain sorted `#89`_
* Reduce size of generated html code `#125`_
* Allow users to copy shared workouts from others `#127`_
* Added breadbrumbs, to make navigation easier `#101`_
* Add option to delete workout sessions and their logs `#156`_
* Improve installation, development and maintenance documentation `#114`_

Other improvements and bugfixes:
`#99`_, `#100`_, `#106`_, `#108`_, `#110`_, `#117`_, `#118`_, `#128`_, `#131`_,
`#135`_, `#145`_, `#155`_



.. _#89: https://github.com/wger-project/wger/issues/89
.. _#98: https://github.com/wger-project/wger/issues/98
.. _#99: https://github.com/wger-project/wger/issues/99
.. _#100: https://github.com/wger-project/wger/issues/100
.. _#101: https://github.com/wger-project/wger/issues/101
.. _#102: https://github.com/wger-project/wger/issues/102
.. _#103: https://github.com/wger-project/wger/issues/103
.. _#106: https://github.com/wger-project/wger/issues/106
.. _#108: https://github.com/wger-project/wger/issues/108
.. _#110: https://github.com/wger-project/wger/issues/110
.. _#114: https://github.com/wger-project/wger/issues/114
.. _#115: https://github.com/wger-project/wger/issues/115
.. _#117: https://github.com/wger-project/wger/issues/117
.. _#118: https://github.com/wger-project/wger/issues/118
.. _#119: https://github.com/wger-project/wger/issues/119
.. _#124: https://github.com/wger-project/wger/issues/124
.. _#125: https://github.com/wger-project/wger/issues/125
.. _#127: https://github.com/wger-project/wger/issues/127
.. _#128: https://github.com/wger-project/wger/issues/128
.. _#131: https://github.com/wger-project/wger/issues/131
.. _#135: https://github.com/wger-project/wger/issues/135
.. _#145: https://github.com/wger-project/wger/issues/145
.. _#155: https://github.com/wger-project/wger/issues/155
.. _#156: https://github.com/wger-project/wger/issues/156


1.5
---
**2014-12-16**

New Translations:

* Dutch (many thanks to David Machiels!)
* Portuguese (many thanks to Jefferson Campos!) `#97`_


New features:

* Add support for gym management `#85`_

  * Gym managers can create and manage gyms
  * Trainers can see the gym's users and their routines

* Reduce amount of CSS and JS libraries by using bootstrap as much as possible `#73`_
* Improvements to the REST API `#75`_

  * Add read-write access
  * Add live browsing of the API with django rest framework
  * Improve documentation
  * /api/v1 is marked deprecated

* Show exercise pictures in workout as well
* Detailed view of exercises and workouts in schedule `#86`_
* Support for both metric (kg) and imperial (lb) weight units `#105`_
* Allow the user to delete his account and data `#84`_
* Add contact field to feedback form
* Cleanup translation strings `#94`_
* Python 3 compatibility! `#68`_

Other improvements and bugfixes:
`#51`_, `#76`_, `#80`_, `#81`_, `#82`_, `#91`_, `#92`_, `#95`_, `#96`_


.. _#51: https://github.com/wger-project/wger/issues/51
.. _#68: https://github.com/wger-project/wger/issues/68
.. _#73: https://github.com/wger-project/wger/issues/73
.. _#75: https://github.com/wger-project/wger/issues/75
.. _#76: https://github.com/wger-project/wger/issues/76
.. _#80: https://github.com/wger-project/wger/issues/80
.. _#81: https://github.com/wger-project/wger/issues/81
.. _#82: https://github.com/wger-project/wger/issues/82
.. _#84: https://github.com/wger-project/wger/issues/84
.. _#85: https://github.com/wger-project/wger/issues/85
.. _#86: https://github.com/wger-project/wger/issues/86
.. _#91: https://github.com/wger-project/wger/issues/91
.. _#92: https://github.com/wger-project/wger/issues/92
.. _#94: https://github.com/wger-project/wger/issues/94
.. _#95: https://github.com/wger-project/wger/issues/95
.. _#96: https://github.com/wger-project/wger/issues/96
.. _#97: https://github.com/wger-project/wger/issues/97
.. _#105: https://github.com/wger-project/wger/issues/105


1.4
---

**2014-03-08**

New features and bugfixes:

  * Calendar view to more easily check workout logs
  * Add "gym mode" with timer to log the workout while at the gym
  * Add automatic email reminders for new workouts
  * New iCal export to add workouts and schedules e.g. to google calendar
  * New exercise overview, grouped by equipment
  * Add possibility to write comments and rate the workout
  * Simplify form for new exercises
  * Alternative PDF export of workout without table for entering logs
  * Unified way of specifying license of submitted content (exercises, etc.)



1.3
---

**2013-11-27**


New translations:

  * Bulgarian (many thanks to Lyuboslav Petrov!)
  * Russian (many thanks to Inna!)
  * Spanish

New features and bugfixes:

  * Mobile version of website
  * Add images to the exercises
  * Exercises now can list needed equipment (barbell, etc.)
  * BMI calculator
  * Daily calories calculator
  * New management utility for languages
  * Improved performance
  * RESTful API



1.2
---
**2013-05-19**

New features and bugfixes:

  * Added scheduling option for workouts.
  * Open all parts of website to all users, this is done by a custom middleware
  * Regular users can submit exercises and ingredients to be included in the general list
  * Add more 'human' units to ingredients like '1 cup' or '1 slice'
  * Add nutritional values calculator on the ingredient detail page
  * Several bugfixes
  * Usability improvements


1.1.1
-----
**2013-03-06**


New features and bugfixes:

  * Pin version of app django_browserid due to API changes in 0.8
  * Fix issue with tabs on exercise overview due to API changes in JQuery


1.1
---
**2013-02-23**

New features and bugfixes:

  * Better navigation bar
  * Added descriptions for the exercises (German)
  * New workout logbook, to keep track of your improvements
  * Import your weight logs from a spreadsheet (CSV-Import)
  * Better filtering for weight chart
  * Muscle overview with corresponding exercises
  * Add guest accounts by generating a temporary user
  * Description pages about the software
  * Easier installation process


1.0.3
-----
**2012-11-19**


New features and bugfixes:

  * Add option to copy (duplicate) workouts and nutritional plans
  * Login without an account with [[https://login.persona.org/|mozilla's Persona]] (BrowserID)
  * Better AJAX handling of the modal dialogs, less page reloads and redirects
  * Expand the list of ingredients in German
  * Add a pagination to ingredient list
  * Improvements to user page:

    * Add a "reset password" link to the login page
    * Email is now user editable

  * More natural lines in weight chart with cubic interpolation


1.0.2
-----
**2012-11-02**

Bugfix release


1.0.1
-----
**2012-11-02**


New features and bugfixes:

  * Fix issue with password change
  * Small improvements to UI
  * Categories editable/deletable from exercise overview page
  * Exercise AJAX search groups by category
  * More tests!
  * Use generic views for editing, creating and deleting objects


1.0
---
**2012-10-16**

Initial release.

New features and bugfixes:

  * Workout manager
  * PDF output for logging progress
  * Initial data with the most popular exercises
  * Simple weight chart
  * Nutrition plan manager
  * Simple PDF output
  * Initial data with nutritional values from the USDA

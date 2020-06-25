.. _codingstyle:

Coding Style Guide
==================

Python
------

Code according to PEP8, but with but with a maximum line length of 100.


Javascript
----------

* Follow AirBnB ES5 style guide, with the following changes:

  * Disallow named function expressions, except in recursive functions, where a name is needed.
  * Console logging is allowed

* Functions called from Django templates need to start with ``wger``


Automatic coding style checks
-----------------------------

The coding style is automatically checked by GitHub actions after sending a
pull request.

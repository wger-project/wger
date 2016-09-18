.. _codingstyle:

Coding Style Guide
==================

Python
------

* Code according to PEP8

  Check that the code is structured as per pep8 but with a maximum line
  length of 100.

* Code for Python 3

  While the application should remain compatible with python2, use django's
  suggestion to mantain sanity: code for py3 and treat py2 as a backwards
  compatibility requirement. If you need, you can use six.


Javascript
----------

* Follow AirBnB ES5 style guide, with the following changes:

  * Disallow named function expressions, except in recursive functions, where a name is needed.
  * Console logging is allowed

* Functions called from Django templates need to start with ``wger``


Check Coding Style
==================

The coding style is automatically check by Travis-CI. To manually check your
files you can run the following commands:

* Python: ``pep8 wger``
* Javascript: ``./node_modules/.bin/gulp lint-js`` (or just ``gulp lint-js`` if
  you installed the node libraries globally on your system)

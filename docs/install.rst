.. _install:

Installation
============

This file gives a broad description of the necessary steps to install wger
on a debian based linux distribution. If your setup differs (e.g. in Red Hat
based distros the package names are slightly different) you will need to
change the steps but in the end, this is a regular django application so it
should run wherever django runs.

The application is compatible and regularly tested with

* sqlite, postgres
* python 2.7, 3.4 and 3.5

You might also want to take a look at the :ref:`other-changes` section for other
changes you might want to do to your local instance such as Terms of Service or
contact page.

.. note::
    Please note that all the steps related to upgrading the database or
    downloading external JS dependencies mentioned in the :ref:`tips` section
    in the development page apply to all the installation options.



Base
----

These are the necessary packages for both development and production
(node and npm are only used to download JS and CSS libraries)::

    sudo apt-get install nodejs nodejs-legacy npm git \
                         python-virtualenv python3-dev \
                         libjpeg8-dev zlib1g-dev libwebp-dev

.. note::
    The application is developed with python 3, which these installation
    instructions also use. If you want to use python 2.7, make sure you install
    the appropriate packages (e.g. python-dev instead of python3-dev, etc.)!


Development
-----------

For development consult the :doc:`development` section.


Production
----------

For a more production-like setting with apache and mod-wsgi consult the
:doc:`production` chapter.


Docker
------

There are also docker images available, see the :doc:`docker` chapter.

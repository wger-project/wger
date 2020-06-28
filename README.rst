docker run -ti -v /path/to/this/checkout:/home/wger/src --name wger.devel --publish 8000:8000 wger/develThank you for downloading wger Workout Manager. wger (ˈvɛɡɐ) is a free, open source web
application that manages your exercises and personal workouts, weight and diet
plans. It can also be used as a simple gym management utility, providing different
administrative roles (trainer, manager, etc.). It offers a REST API as well, for
easy integration with other projects and tools.

It is written with python/django and uses jQuery and some D3js for charts.

For more details and a live system, refer to the project's site: https://wger.de/


Installation
============

These are the basic steps to install and run the application locally on a Linux
system. There are more detailed instructions, other deployment options as well
as an administration guide available at https://wger.readthedocs.io or locally
in your code repository in the docs folder (``make html`` to compile, then open
_build/index.html).

Please consult the commands' help for further information and available
parameters.


Docker
------

Useful to just try it out. Check the documentatio on how to use docker for
development::

    docker run -ti --name wger.apache --publish 8000:80 wger/apache

Then just open http://localhost:8000 and log in as: **admin**, password **admin**


Development version (from git)
------------------------------

**Note:** You can safely install from master, it is almost always in a usable
and stable state.


1) Install the necessary packages

::

 $ sudo apt-get install python3-dev nodejs npm git


Then install the python packages from pypi in the virtualenv::

 $ python3 -m venv venv-django
 $ source venv-django/bin/activate


2) Start the application. This will download the required JS and CSS libraries
   and create a SQlite database and populate it with data on the first run.

::

 $ git clone https://github.com/wger-project/wger.git
 $ cd wger
 $ pip install --upgrade pip
 $ pip install -r requirements.txt  # or requirements_devel.txt to develop
 $ npm install
 $ npm install bower
 $ python setup.py develop
 $ wger create_settings \
        --settings-path /path/to/current/folder/settings.py \
        --database-path /path/to/current/folder/database.sqlite
 $ wger bootstrap \
        --settings-path /path/to/current/folder/settings.py \
        --no-start-server
 $ python manage.py runserver

3) Log in as: **admin**, password **admin**

After the first run you can just use django's development server::

 $ python manage.py runserver


Stable version (from PyPI)
--------------------------

1) Install the necessary packages and their dependencies in a virtualenv

::

 $ sudo apt-get install python3-dev nodejs npm git
 $ python3 -m venv venv-django
 $ source venv-django/bin/activate
 $ pip install wger


2) Start the application. This will download the required JS and CSS libraries
   and create a SQlite database and populate it with data on the first run.
   Then, log in as: **admin**, password **admin**

::

  $ wger bootstrap


3) To start the installation again, just call wger start

::

  $ wger start


Command line options
--------------------
You can get a list of all available commands by calling ``wger`` without any
arguments::

    Available tasks:

    bootstrap               Performs all steps necessary to bootstrap the application
    config_location         Returns the default location for the settings file and the data folder
    create_or_reset_admin   Creates an admin user or resets the password for an existing one
    create_settings         Creates a local settings file
    load_fixtures           Loads all fixtures
    migrate_db              Run all database migrations
    start                   Start the application using django's built in webserver

You can also get help on a specific command with ``wger --help <command>``.

Contact
=======

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* **gitter:** https://gitter.im/wger-project/wger
* **issue tracker:** https://github.com/wger-project/wger/issues
* **twitter:** https://twitter.com/wger_de
* **mailing list:** https://groups.google.com/group/wger / wger@googlegroups.com,
  no registration needed


Sources
=======

All the code and the content is freely available:

* **Main repository:** https://github.com/wger-project/wger


Donations
=========
wger is free software and will always remain that way. However, if you want to
help and support the project you are more than welcome to donate an amount of
your choice.

.. image:: https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif
   :target: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=UPMWQJY85JC5N

License
=======

The application is licensed under the Affero GNU General Public License 3 or
later (AGPL 3+).

The initial exercise and ingredient data is licensed additionally under one of
the Creative Commons licenses, see the individual exercises for more details.

The documentation is released under a CC-BY-SA: either version 4 of the License,
or (at your option) any later version.

Some images were taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

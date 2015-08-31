Thank you for downloading wger Workout Manager. wger is a free, open source web
application that manages your exercises and personal workouts, weight and diet
plans. It can also be used as a simple gym management utility, providing different
administrative roles (trainer, manager, etc.). It offers a REST API as well, for
easy integration with other projects and tools.

It is written with python/django and uses jQuery and some D3js for charts.

For more details and a live system, refer to the project's site: https://wger.de/

There are more detailed instructions, other deployment options as well as an
administration guide available at https://wger.readthedocs.org or locally in
your code repository in the docs folder (``make html`` to compile, then open
_build/index.html).


Installation
============

These are the basic steps to install and run the application locally on a linux
system.


Development version (from git)
------------------------------

**Note:** You can safely install from master, it is almost always in a usable and stable
state.


1) Install the necessary packages and their dependencies in a virtualenv

::

 $ sudo apt-get install python-dev python-virtualenv nodejs
 $ virtualenv venv-django
 $ source venv-django/bin/activate
 $ npm install bower

2) Start the application. This will create a SQlite database and populate it
   with data on the first run.

::

 $ git clone https://github.com/rolandgeider/wger.git
 $ cd wger
 $ pip install -r requirements.txt  # or requirements_devel.txt to develop
 $ python manage.py bower install
 $ python start.py

 # After the first run you can just use django's development server
 $ python manage.py runserver

3) Log in as: **admin**, password **admin**

Stable version (from PyPI)
--------------------------

1) Install the necessary packages and their dependencies in a virtualenv

::

 $ sudo apt-get install python-dev python-virtualenv
 $ virtualenv venv-django
 $ source venv-django/bin/activate
 $ pip install wger


2) Start the application. This will create a SQlite database and populate it
   with data on the first run

::

 $ wger


3) Log in as: **admin**, password **admin**


Command line options
--------------------

The available options for the ``wger`` command (if installed from PyPI) or
``start.py`` (if installed from source) are the following ::

 Usage: main.py [options]

 Run wger Workout Manager using django's builtin server

 Options:
  -h, --help            show this help message and exit
  -a ADDRESS, --address=ADDRESS
                        IP Address to listen on.
  -p PORT, --port=PORT  Port to listen on.
  --syncdb              Update/create database before starting the server.
  --reset-admin         Make sure the user 'admin' exists and uses 'admin' as
                        password.
  -s SETTINGS, --settings=SETTINGS
                        Path to the wger configuration file.
  --no-reload           Do not reload the development server.
  --no-browser          Do not open the application in a browser.
  --version             Show version and exit.
  --show-config         Show configuration paths and exit.

Contact
=======

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected (in this case you can also open a ticket on the
issue tracker).

* **twitter:** https://twitter.com/wger_de
* **mailing list:** https://groups.google.com/group/wger / wger@googlegroups.com,
  no registration needed
* **IRC:** channel #wger on freenode.net, webchat: http://webchat.freenode.net/?channels=wger
* **issue tracker:** https://github.com/rolandgeider/wger/issues


Sources
=======

All the code and the content is freely available:

* **Main repository:** https://github.com/rolandgeider/wger
* **Mirror:** https://bitbucket.org/rolandgeider/wger


Licence
=======

The application is licenced under the Affero GNU General Public License 3 or
later (AGPL 3+).

The initial exercise and ingredient data is licensed additionally under a
Creative Commons Attribution Share-Alike 3.0 (CC-BY-SA 3.0)

The documentation is released under a CC-BY-SA either version 4 of the License,
or (at your option) any later version.

Some images where taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

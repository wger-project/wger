Thank you for downloading wger Workout Manager. Workout Manager is a free, open
source web application that manages your exercises, workouts, weight and diet
plans.

For more details and a live system, refer to the project's site: http://wger.de/


Installation
============

These are the basic steps to get the application running. There are more
detailed installation instructions on http://wger.de/en/software/code

1) Install the necessary packages and their dependencies

.. code:: bash

 $ sudo apt-get install python-virtualenv
 $ sudo apt-get install python-dev
 $ virtualenv python-django
 $ source python-django/bin/activate
 $ pip install wger


2) Start the application. This will create a SQlite database and populate it with data on the first run


.. code:: bash

 $ wger


3) Log in as: **admin**, password **admin**


Command line options
--------------------

The available options for the ``wger`` command are ::

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
  --version             Show version and exit.
  --show-config         Show configuration paths and exit.

Contact
=======

Feel free to write me an email (``roland [at] geider [dot] net``) if you found
this useful or if there was something that didn't behave as you expected.
Alternatively, you can also open a ticket on the bitbucket tracker:
https://bitbucket.org/rolandgeider/workout_manager/issues


Sources
=======

All the code and the content is freely available:

* **Main repository**: HG, https://bitbucket.org/rolandgeider/workout_manager
* **Mirror**: GIT, https://github.com/rolandgeider/workout_manager


Licence
=======

The application is licenced under the Affero GNU General Public License 3 or later
(AGPL 3+).

The initial exercise and ingredient data is licensed additionally under a
Creative Commons Attribution Share-Alike 3.0 (CC-BY-SA 3.0)

The YAML CSS framework is licensed under a Creative Commons Attribution 2.0
License (CC-BY 2.0)

Some images where taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

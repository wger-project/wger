.. _development:

Development
===========

Requirements
------------

Get the code
~~~~~~~~~~~~

The code is available on Github::

  $ git clone https://github.com/wger-project/wger.git

Create a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's a best practise to create a Python virtual environment::

  $ virtualenv --python python3 venv-wger
  $ source venv-wger/bin/activate
  $ cd wger


Install Requirements
~~~~~~~~~~~~~~~~~~~~

To install the Python requirements::

  $ pip install -r requirements_devel.txt

Install NodeJS and npm::
Follow the instructions on the `NPM website <https://docs.npmjs
.com/getting-started/installing-node>`_ and make sure to use Node LTS (4
.x).

Install the npm modules::

  $ npm install


Install site
~~~~~~~~~~~~

To install the server::

  $ invoke create_settings \
           --settings-path /home/wger/wger/settings.py \
           --database-path /home/wger/wger/database.sqlite
  $ invoke bootstrap_wger \
           --settings-path /home/wger/wger/settings.py \
           --no-start-server

Start the server
----------------

To start the server::

  $ python manage.py runserver

That's it. You can log in with the default administator user:

* **username**: admin
* **passsword**: admin

You can start the application again with the django server with
``python manage.py runserver``.

.. _tips:

Tips
----

Updating the code
~~~~~~~~~~~~~~~~~

When pulling updates from upstream there are a couple of things to consider.
These steps apply to all installation methods above.

Upgrading the database
``````````````````````

There are regularly changes and upgrades to the database schema (these may also
come from new versions of django or the installed dependencies). If you start
the development server and see a message that there are unapplied migrations,
just do ``python manage.py migrate --all``.

Downloading dependencies with Bower
```````````````````````````````````

Bower is used to download different JS and CSS libraries. If you update master
it is recommended that you first delete the existing libraries
(``rm wger/core/static/bower_components``) and then download the new versions
with::

    $ python manage.py bower install


Some info about bower, during the bootstrap process bower is installed locally
to src/wger. If this didn't work and you get an error saying that bower is not
installed, you can manually install it by going to the  project's root directory
and performing the step manually::

   $ cd src/wger
   $ npm install bower

Alternatively, you can manually set the path to the bower binary by editing
``BOWER_PATH`` (see ``wger/settings_global.py``).


Clearing the cache
``````````````````

Sometimes there are changes to the internal changes of the cached structures.
It is recommended that you just clear all the existing caches
``python manage.py clear-cache --clear-all``

Miscellaneous settings
~~~~~~~~~~~~~~~~~~~~~~

The following settings can be very useful during development (add to your
settings.py):


**Setting the email backend**
   Use the console backend, all sent emails will be printed to it::

       EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

Dummy data generator
~~~~~~~~~~~~~~~~~~~~

To properly test the different parts of the application for usability or
performance, it is often very useful to have some data to work with. For this
reason, there is a dummy data generator script in
extras/dummy_generator/generator.py. It allows you to generate entries for
users, gyms, workouts and logs. For detailed usage options do::

  python generator.py --help

Or for options for, e.g. user generation::

  python generator.py users --help

To get you started, you might want to invoke the script in the following way. This
will create 10 gyms and 300 users, randomly assigning them to a different gym. Each
user will have 20 workouts and each exercise in each workout 30 log entries::

  python generator.py gyms 10
  python generator.py users 300
  python generator.py workouts 20
  python generator.py logs 30
  python generator.py sessions random
  python generator.py weight 100
  python generator.py nutrition 20

.. note::
   All generated users have their username as password.

.. note::
   While it is possible to generate hundreds of users, gyms are more restricted and
   you will probably get duplicate names if you generate more than a dozen.


Selectively running tests
~~~~~~~~~~~~~~~~~~~~~~~~~

If you do a ``python manage.py test`` you will run the complete testsuite, and
this can take a while. You can control which tests will be executed like this.

Test only the tests in the 'core' app::

  python manage.py test wger.core

Test only the tests in the 'test_user.py` file in the core app::

  python manage.py test wger.core.tests.test_user

Test only the tests in 'StatusUserTestCase' in the file 'test_user.py` file in
the core app::

  python manage.py test wger.core.tests.test_user.StatusUserTestCase


Using runserver_plus
~~~~~~~~~~~~~~~~~~~~

During development you can use ``runserver_plus`` instead of the default django
server as you can use an interactive debugger directly from the browser if an
exception occurs. It also accepts the same command line options. For this just
install the following packages::

    pip install django_extensions werkzeug
    python manage.py runserver_plus [options]


Contributing
------------

* **Send pull requests**: for new code you want to share, please send pull
  requests in github. Sending patches by email or attaching them to an issue
  means a lot more of work. It's recommended that you work on a feature branch
  when working on something, specially when it's something bigger. While many
  people insist on rebasing before sending a pull request, it's not necessary.

* **Run the tests**: wger is proud to have a test coverage of over 90%. When you
  implement something new, don't forget to run the testsuite and write approriate
  tests for the new code. If you use github, configure the awesome Travis CI,
  there is already a .travis file in the sources.

* **Code according to the coding style**: :ref:`codingstyle`

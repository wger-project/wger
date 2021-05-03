.. _tips:

Tips and tricks
---------------

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

Downloading JS and CSS libraries
````````````````````````````````

We use yarn to download the JS and CSS libraries. To update them just go to
the source and do ::

        $ yarn install

This happens automatically during the bootstrap process.


Updating SASS files
```````````````````
After updating the SASS files, you need to compile them to regular CSS::

    yarn build:css:sass


Clearing the cache
``````````````````

Sometimes there are changes to the internal changes of the cached structures.
It is recommended that you just clear all the existing caches
``python manage.py clear-cache --clear-all`` or just set the timeout to something
like one second (in settings.py::

    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wger-cache',
        'TIMEOUT': 1
        }
    }

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
user will have 20 workouts and each exercise in each workout 30 log entries as well
as 10 nutrition diary entries per day::

  python generator.py gyms 10
  python generator.py users 300
  python generator.py workouts 20
  python generator.py logs 30
  python generator.py sessions random
  python generator.py weight 100
  python generator.py nutrition 20
  python generator.py nutrition-diary 10

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
  implement something new, don't forget to run the testsuite and write appropriate
  tests for the new code.

* **Code according to the coding style**: :ref:`codingstyle`

.. _development:

Development
===========

First, install all required packages::

  $ sudo apt-get install python-virtualenv python-dev nodejs
  $ virtualenv python-django
  $ source python-django/bin/activate
  $ pip install -r requirements_devel.txt
  $ npm install bower

.. note::
   For python3 some packages have slightly different names such as ``python3-dev``


Get the code and start the application. This will create a SQlite database
and populate it with data on the first run::

  $ git clone https://github.com/rolandgeider/wger.git
  $ cd wger
  $ python manage.py bower install
  $ python start.py

That's it. You can log in with the default administator user:

* **username**: admin
* **passsword**: admin

You can start the application again with the django server with
``python manage.py runserver``. If you pull updates and there were database
changes, you can apply them with a simple ``python manage.py migrate --all``.

Tips
----

Moving important files
~~~~~~~~~~~~~~~~~~~~~~

The start script places the settings file and the sqlite database in a non
obvious place. For development I suggest moving them to the folder with the
code::

    $ cd wger
    $ python start.py --show-config
    Settings file: /home/user/.config/wger/settings.py
    Database file: /home/user/.local/share/wger/database.sqlite
    
    $ mv /home/user/.config/wger/settings.py .
    $ mv /home/user/.local/share/wger/database.sqlite

    $ vim settings.py
    # Update the path for the sqlite files in DATABASES section


Miscelaneous settings
~~~~~~~~~~~~~~~~~~~~~

The following settings can be very useful during development (add to your
settings.py):


**Setting the email backend**
   Use the console backend, all sent emails will be printed to it::

       EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


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

.. note::
   All generated users have their username as password.

.. note::
   While it is possible to generate hundreds of users, gyms are more restricted and
   you will probably get duplicate names if you generate more than a dozen.

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

* **Code according to PEP8**: check that the code is structured as per pep8 but
  with a maximum line length of 100. This can be checked automatically with the
  pep8 tool (pip install pep8) from the command line (travis will do this as part 
  of the tests): ``pep8 wger``

* **code for python3**: while the application should remain compatible with
  python2, use django's suggestion to mantain sanity: code for py3 and treat
  py2 as a backwards compatibility requirement. If you need, you can use six.
  
For other ways of contributing besides code, you might want to take a look at
the contribute page.

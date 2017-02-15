Commands
========

Please note that the administration commands are intended e.g. to bootstrap/install
an application to a new system, while the management ones are made to administer a
running application (to e.g. delete guest users, send emails, etc.).

Administration Commands
-----------------------

The application provides several administration and bootstraping commands. They
are all available with ``wger`` (if installed from PyPI) or ``invoke`` (if
installed from source)::

    wger <command>

or ::

    invoke <command>

Both versions behave the same but for simplicity, the invoke version will be used
in this manual.


You can get a list of all available commands with ``invoke --list`` or ``wger``.
While you can do this from any folder in the application, some of them (e.g.
``start_wger``) might only work from the root folder::

    Available tasks:

    bootstrap_wger          Performs all steps necessary to bootstrap the application
    config_location         Returns the default location for the settings file and the data folder
    create_or_reset_admin   Creates an admin user or resets the password for an existing one
    create_settings         Creates a local settings file
    load_fixtures           Loads all fixtures
    migrate_db              Run all database migrations
    start_wger              Start the application using django's built in webserver

You can also get help on a specific command with ``invoke --help <command>``.

.. note::
    Most commands support a ``--settings-path`` command line option that sets the
    settings file to use for the operation. If you use it, it is recommended to
    use absolute paths, for example::

        invoke bootstrap_wger --settings-path /path/to/development/wger/settings-test.py



Bootstrap wger
~~~~~~~~~~~~~~

Command: **bootstrap_wger**

This command bootstraps the application: it creates a settings file, initialises
a sqlite database, loads all necessary fixtures for the application to work and
creates a default administrator user. While it can also work with e.g. a postgreSQL
database, you will need to create it yourself::

    invoke bootstrap_wger

The most usual use-case is creating the settings file and the sqlite database to
their default locations, but you can set your own paths if you want e.g. start
developing on a branch that is going to change the database schema.

Usage::

    Usage: inv[oke] [--core-opts] bootstrap_wger [--options] [other tasks here ...]

    Docstring:
      Performs all steps necessary to bootstrap the application

    Options:
      -a STRING, --address=STRING         Address to use. Default: localhost
      -b, --browser                       Whether to open the application in a browser window. Default: false
      -d STRING, --database-path=STRING   Path to sqlite database (absolute path recommended). Leave empty for default
      -p, --port                          Port to use. Default: 8000
      -s STRING, --settings-path=STRING   Path to settings file (absolute path recommended). Leave empty for default


Start wger
~~~~~~~~~~

Command: **start_wger**

Starts an already installed application::

    invoke start_wger

Please note that this is simply a comfort function and does not use any *magic*,
it simply calls django's development server and (optionally) opens a browser
window. If you are developing, using the usual ``python manage.py runserver``
is probably better.

Usage::

    Usage: inv[oke] [--core-opts] start_wger [--options] [other tasks here ...]

    Docstring:
      Start the application using django's built in webserver

    Options:
      -a STRING, --address=STRING         Address to bind to. Default: localhost
      -b, --browser                       Whether to open the application in a browser window. Default: false
      -e STRING, --extra-args=STRING      Additional arguments to pass to the builtin server. Pass as string: "--arg1 --arg2=value". Default: none
      -p, --port                          Port to use. Default: 8000
      -s STRING, --settings-path=STRING   Path to settings file. Leave empty for default
      -t, --[no-]start-server             Whether to start the development server. Default: true


Default locations
~~~~~~~~~~~~~~~~~

Command: **config_location**

Information command that simply outputs the default locations for the settings
file as well as the data folder used for the sqlite database and the uploaded
files.


Create settings
~~~~~~~~~~~~~~~

Command: **create_settings**

Creates a new settings file based. If you call it without further arguments it
will create the settings in the default locations::

    invoke create settings

If you pass custom paths, it's recommended to use absolute paths::

    invoke create_settings --settings-path /path/to/development/wger/settings-test.py --database-path /path/to/development/wger/database-test.sqlite


Usage::

    Usage: inv[oke] [--core-opts] create_settings [--options] [other tasks here ...]

    Docstring:
      Creates a local settings file

    Options:
      -a STRING, --database-type=STRING   Database type to use. Supported: sqlite3, postgresql. Default: sqlite3
      -d STRING, --database-path=STRING   Path to sqlite database (absolute path recommended). Leave empty for default
      -k, --key-length                    Lenght of the generated secret key. Default: 50
      -s STRING, --settings-path=STRING   Path to settings file (absolute path recommended). Leave empty for default
      -u STRING, --url=STRING



Create or reset admin
~~~~~~~~~~~~~~~~~~~~~

Command: **create_or_reset_admin**

Makes sure that the default administrator user exists. If you change the password
it is reset.


Usage::

    Usage: inv[oke] [--core-opts] create_or_reset_admin [--options] [other tasks here ...]

    Docstring:
      Creates an admin user or resets the password for an existing one

    Options:
      -s STRING, --settings-path=STRING   Path to settings file (absolute path recommended). Leave empty for default



Migrate database
~~~~~~~~~~~~~~~~

Command: **migrate_db**

Migrates the database schema. This command is called internally when installing
the application. The only need to call this explicitly is after installing a new
version of the application.

Calling this command is a safe operation, if your database is current, nothing
will happen.


Usage::

    Usage: inv[oke] [--core-opts] migrate_db [--options] [other tasks here ...]

    Docstring:
      Run all database migrations

    Options:
      -s STRING, --settings-path=STRING   Path to settings file (absolute path recommended). Leave empty for default



Load all fixtures
~~~~~~~~~~~~~~~~~

Command: **load_fixtures**

Loads all fixture file with the default data. This data includes all data necessary
for the application to work such as:

* exercises, muscles, equipment
* ingredients, units
* languages
* permission groups
* etc.

This command is called internally when installing the application but you can use
it to reset the data to the original state. Note: new entries or user entries such
as workouts are *not* reset with this, only the application data.

Usage::

    Usage: inv[oke] [--core-opts] load_fixtures [--options] [other tasks here ...]

    Docstring:
      Loads all fixtures

    Options:
      -s STRING, --settings-path=STRING   Path to settings file (absolute path recommended). Leave empty for default





Management commands
-------------------

wger also implements a series of django commands that perform different
management functions that are sometimes needed. Call them with
``python manage.py <command_name>``:

**download-exercise-images**
  synchronizes the exercise images from wger.de to the local installation. Read
  its help text as it could save the wrong image to the wrong exercise should
  different IDs match.

**redo-capitalize-names**
  re-calculates the capitalized exercise names. This command can be called if the
  current "smart" capitalization algorithm is changed. This is a safe operation,
  since the original names (as entered by the user) are still available.

**submitted-exercises**
  simply prints a list of user submitted exercises

**extract-i18n**
  extract strings from the database that have to be inserted manually in the PO
  file when translating. These include e.g. exercise categories.

**clear-cache**
  clears different application caches. Might be needed after some updates or
  just useful while testing. Please note that you must select what caches to
  clear.

**update-user-cache**
  update the user cache-table. This command is only needed when the python code
  used to calculate any of the cached entries is changed and the ones in the
  database need to be updated to reflect the new logic.



Cron
~~~~

The following commands are built to be called regularly, via a cronjob or
similar

**delete-temp-users**
  deletes all guest users older than 1 week. At the moment this value can't be
  configured

**email-reminders**
  sends out email reminders for user that need to create a new workout.

**email-weight-reminders**
  sends out email reminders for user that need to enter a new (body) weight entry.

**inactive-members**
  Sends email for gym members that have not been to the gym for a specified
  amount of weeks.

.. _development:

Development
===========

You can safely install from master, it is almost always in a usable
and stable state.

Virtual environment
~~~~~~~~~~~~~~~~~~~

::

  $ python3 -m venv venv-wger
  $ source venv-wger/bin/activate


Get the code
~~~~~~~~~~~~
::

  $ git clone https://github.com/wger-project/wger.git src
  $ cd src

Install Requirements
~~~~~~~~~~~~~~~~~~~~
::

  $ pip install -r requirements_dev.txt
  $ npm install -g yarn sass
  $ python setup.py develop

Install application
~~~~~~~~~~~~~~~~~~~

This will download the required JS and CSS libraries and create a SQlite
database and populate it with data on the first run::


  $ wger create-settings
  $ wger bootstrap
  $ wger load-online-fixtures

You can of course also use other databases such as postgres or mariaDB. Create
a database and user and edit the DATABASES settings before calling bootstrap.
Take a look at the :ref:`prod_postgres` on apache on how that could look like.

Start the server
----------------

After the first run you can just use django's development server::

  $ python manage.py runserver

That's it. You can log in with the default administrator user:

* **username**: admin
* **password**: adminadmin

You can start the application again with the django server with
``python manage.py runserver``.

.. _development:

Development
===========

Virtual environment
~~~~~~~~~~~~~~~~~~~

Create a new virtualenv::

  $ python3 -m venv venv-wger
  $ source venv-wger/bin/activate


Get the code
~~~~~~~~~~~~

Download the source code::

  $ git clone https://github.com/wger-project/wger.git src
  $ cd src

Install Requirements
~~~~~~~~~~~~~~~~~~~~

Install python requirements::

  $ pip install -r requirements_dev.txt
  $ python setup.py develop

Install application
~~~~~~~~~~~~~~~~~~~

This will download the required JS and CSS libraries and create an SQLite
database and populate it with data on the first run::


  $ wger create-settings
  $ wger bootstrap
  $ wger load-online-fixtures

You can of course also use other databases such as PostgreSQL or MariaDB. Create
a database and user and edit the DATABASES settings before calling bootstrap.
Take a look at the :ref:`prod_postgres` on apache on how that could look like.

Start the server
----------------

After the first run you can just use Django's development server::

  $ python manage.py runserver

That's it. You can log in with the default administrator user:

* **username**: admin
* **password**: adminadmin

You can reset the admin's password with ``wger create-or-reset-admin``.

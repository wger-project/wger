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
  $ python setup.py develop

Install application
~~~~~~~~~~~~~~~~~~~

To install the development server, init the databasse and create a settings
file::

  $ wger create_settings \
           --settings-path /home/wger/wger/settings.py \
           --database-path /home/wger/wger/database.sqlite
  $ wger bootstrap \
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

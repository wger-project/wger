.. _install:

Installation (production)
=========================

This file gives a broad description of the necessary steps to install wger on a
production environment with apache as a webserver. Since this is a regular
django application, refer to its documentation if your setup differs. For a
development setup refer to :doc:`development`

The application is compatible and regularly tested with

* sqlite, postgres
* python 2.7, 3.3, 3.4 and 3.5

See the :ref:`other-changes` section for content related changes to your
installation.



Databasse
---------

postgreSQL
~~~~~~~~~~

Install the postgres server and create a database and a user::

    createdb wger
    psql wger
    CREATE USER wger;
    GRANT ALL PRIVILEGES ON DATABASE wger to wger;


sqlite
~~~~~~

No further steps necessary.


Apache
------

Install apache and the WSGI module::

  sudo apt-get install apache2 libapache2-mod-wsgi-py3 nodejs npm
  sudo vim /etc/apache2/apache2.conf


Configure apache to serve the application::

  >>>
  WSGIScriptAlias / /home/myuser/wger/wger/wsgi.py
  WSGIPythonPath /home/myuser/wger:/home/myuser/venv-wger/lib/python3.4/site-packages

  <Directory /home/myuser/wger>
      <Files wsgi.py>
          Require all granted
      </Files>
  </Directory>


  <VirtualHost *:80>
      Alias /static/ /home/myuser/static/
      <Directory /home/myuser/static>
          Require all granted
      </Directory>

      Alias /media/ /home/myuser/media/
      <Directory /home/myuser/media/>
          Require all granted
      </Directory>

      ErrorLog ${APACHE_LOG_DIR}/error.log
      CustomLog ${APACHE_LOG_DIR}/access.log combined
  </VirtualHost>



Application
-----------

Install the necessary packages to create a virtualenv for python (note that you
might need to install more if you want the thumbnailer to be able to support
more image formats, consult the documentation for pillow for more details)::

  sudo apt-get install git python3-dev python-virtualenv
  virtualenv --python python3 venv-wger
  source venv-wger/bin/activate

If using sqlite, create a folder for it (must be writable by the apache user
so you can just give it the folder with chown):: 

  mkdir db
  chmod o+w db
  
  touch db/database.sqlite
  chmod o+w database.sqlite



Create folders to collect all static resources and save uploaded files (must
be readable by the apache process)::

  mkdir static

  mkdir media
  chmod o+w media

Get the application::

  git clone https://github.com/rolandgeider/wger.git
  cd wger
  pip install -r requirements.txt
  npm install bower
  invoke create_settings --settings-path ./settings.py

Edit your ``settings.py`` file and set the database, ``SITE_URL``,
``STATIC_ROOT`` and ``MEDIA_ROOT``::


      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': u'/home/myuser/db/database.sqlite',
          'USER': '',
          'PASSWORD': '',
          'HOST': '',
          'PORT': '',
      }
  }

  >>> SITE_URL anpassen
  >>> STATIC_ROOT = '/home/myuser/static'
  >>> MEDIA_ROOT = '/home/myuser/wger/media'

Run the installation scritpt, this will load all initial data::

  invoke bootstrap_wger --settings-path /path/to/settings.py --no-start-server


Start.py will create a default administator user (you probably want to change
the password as soon as you log in):

* **username**: admin
* **password**: admin

Collect all static resources:: 

  python manage.py collectstatic


.. _other-changes:

Other changes
-------------

If you want to use the application as a public instance, you will probably want to
change the following templates:

* **tos.html**, for your own Terms Of Service here
* **about.html**, for your contact address or other such legal requirements

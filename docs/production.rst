Production
==========

Wger user
---------

It is recommended to add a dedicated user for the application::

    sudo adduser wger --disabled-password --gecos ""

The following steps assume you did, but it is not necessary (nor is it
necessary to call it 'wger'). In that case, change the paths as needed.

Apache
------

Install apache and the WSGI module::

  sudo apt-get install apache2 libapache2-mod-wsgi-py3
  sudo vim /etc/apache2/sites-available/wger.conf


Configure apache to serve the application::

    <Directory /home/wger/src>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>


    <VirtualHost *:80>
        WSGIDaemonProcess wger python-path=/home/wger/src:/home/wger/venv/lib/python3.4/site-packages
        WSGIProcessGroup wger
        WSGIScriptAlias / /home/wger/src/wger/wsgi.py

        Alias /static/ /home/wger/static/
        <Directory /home/wger/static>
            Require all granted
        </Directory>

        Alias /media/ /home/wger/media/
        <Directory /home/wger//media>
            Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Apache has a problem when uploading files that have non-ASCII characters, e.g.
for exercise images. To avoid this, add to /etc/apache2/envvars (if there is
already an ``export LANG``, replace it)::

    export LANG='en_US.UTF-8'
    export LC_ALL='en_US.UTF-8'


Activate the settings and disable apache's default::

    sudo a2dissite 000-default.conf
    sudo a2ensite wger
    sudo service apache2 reload

Database
---------

postgreSQL
~~~~~~~~~~

Install the postgres server and create a database and a user::

    sudo apt-get install postgresql postgresql-server-dev-9.3 # or appropriate version
    su - postgres
    createdb wger
    psql wger -c "CREATE USER wger WITH PASSWORD 'wger'";
    psql wger -c "GRANT ALL PRIVILEGES ON DATABASE wger to wger";

You might want or need to edit your ``pg_hba.conf`` file to allow local socket
connections or similar.


sqlite
~~~~~~

If using sqlite, create a folder for it (must be writable by the apache user)::

  mkdir db
  touch db/database.sqlite
  chmod -R o+w db

Application
-----------

Make a virtualenv for python and activate it::

  virtualenv --python python3 /home/wger/venv
  source /home/wger/venv/bin/activate

Create folders to collect all static resources and save uploaded files. The
``static`` folder will only contain CSS and JS files, so it must be readable
by the apache process while ``media`` will contain the uploaded files and must
be writeable as well::

  mkdir static

  mkdir media
  chmod o+w media

Get the application::

  git clone https://github.com/wger-project/wger.git /home/wger/src
  cd /home/wger/src
  npm install bower
  pip install -r requirements.txt
  pip install psycopg2 # Only if using postgres
  invoke create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite

If you are using postgres, you need to edit the settings file and set the
correct values for the database (use ``django.db.backends.postgresql_psycopg2``
for the engine). Also set ``MEDIA_ROOT`` to ``/home/wger/media`` and
``STATIC_ROOT`` to ``/home/wger/static``.

Run the installation script, this will download some CSS and JS libraries and
load all initial data::

  invoke bootstrap_wger --settings-path /path/to/settings.py --no-start-server


Collect all static resources::

    python manage.py collectstatic


The bootstrap command will also create a default administrator user (you probably
want to change the password as soon as you log in):

* **username**: admin
* **password**: admin


.. _other-changes:

Other changes
-------------

If you want to use the application as a public instance, you will probably want to
change the following templates:

* **tos.html**, for your own Terms Of Service here
* **about.html**, for your contact address or other such legal requirements

.. _updating:

Updating the application
========================
To keep the application updated you need to regularly perform the following
steps well you pull from upstream.


Python dependencies
```````````````````
To install updated python dependencies::

    source /path/to/venv/bin/activate
    python manage.py migrate


Upgrade the database
````````````````````````````````
There are regular changes and upgrades to the database schema (these may also
come from new versions of Django or the installed dependencies). If you start
your server and see a message that there are unapplied migrations, just do::

    python manage.py migrate --all

You might want to save a dump of the database before applying the migrations
in case something happens.


JS and CSS dependencies
````````````````````````````````
We use yarn to download the JS and CSS libraries. To update them just run
the following command on the source folder::

    yarn install
    yarn build:css:sass
    python manage.py collectstatic # only needed in production

Pull new data
`````````````

You can pull new exercise data and ingredients but remember that new ingredients
can overwrite the ones you added manually::

  python3 manage.py sync-exercises
  python3 manage.py download-exercise-images
  wger load-online-fixtures


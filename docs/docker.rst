Docker
======

There are docker files available to quickly get a version of wger up and
running. They are all located under ``extras/docker`` if you want to build
them yourself.


Development
-----------

This image installs the application using virtualenv, uses a sqlite database
and serves it with django's development server.


First build the image::

    docker build -t wger/devel .

Run a container and start the application::

    docker run -ti --name wger.devel --publish 8000:8000 wger/devel
    (in docker) source ~/venv/bin/activate
    (in docker) python manage.py runserver 0.0.0.0:8000

Now you can access the application on port 8000 of your host (probably just
http://localhost:8000).

Depending on what you intend to do with it, you might want to map a local folder
to the container. This is interesting if e.g. you want to keep the wger source
code on your host machine and use docker only to serve it. Then you can do this::

    docker run -ti \
        --name wger.test1 \
        --publish 8005:8000 \
        --volume /path/to/local/wger/:/home/wger/src \
         wger/devel

It will mount the local path *on top* of the folder in the container, basically
exchanging one for the other. Please note that for this to work you need to
manually checkout the code to ``/path/to/local/wger/`` and create a settings file
as well.


Apache
------

This image runs the application using WSGI and apache.

First build the image::

    docker build --tag wger/apache .

Run a container and start the application::

    docker run -ti --name wger.apache --publish 8000:80 wger/apache

Now you can access the application on port 8000 of your host (probably just
http://localhost:8000).
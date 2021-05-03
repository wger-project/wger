Docker images
=============

There are docker files available to quickly get a version of wger up and
running. They are all located under ``extras/docker`` if you want to build
them yourself.

Note that you need to build from the project's source folder, e.g::

    docker build -f extras/docker/development/Dockerfile -t wger/devel .
    docker build -f extras/docker/apache/Dockerfile --tag wger/apache .


Apache
------

This image runs the application using WSGI and apache.

Get the image::

    docker pull wger/apache

Run a container and start the application::

    docker run -ti --name wger.apache --publish 8000:80 wger/apache

Then just open http://localhost:8000 and log in as: **admin**, password **adminadmin**


Development
-----------

This image installs the application using virtualenv, uses a sqlite database
and serves it with django's development server.

Get the image::

    docker pull wger/devel

Run a container and start the application::

    docker run -ti --name wger.devel --publish 8000:8000 wger/devel
    (in docker) source ~/venv/bin/activate
    (in docker) python manage.py runserver 0.0.0.0:8000

Then just open http://localhost:8000 and log in as: **admin**, password **adminadmin**

As an alternative you might want to map a local folder to the container.
This is interesting if e.g. you want to keep the wger source code on
your host machine and use docker only to serve it. Then do this::

    docker run -ti \
        --name wger.test1 \
        --publish 8005:8000 \
        --volume /path/to/local/wger/:/home/wger/src \
         wger/devel

It will mount the local path *on top* of the folder in the container. For this to
work you obviously need to manually checkout the code to ``/path/to/local/wger/``
and create a settings file as well.


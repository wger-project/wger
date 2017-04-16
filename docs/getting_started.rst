.. _getting_started:

Getting started
===============

You can get a local instance of wger installed in a couple of minutes.

It is recommended to install a development instance or start a docker
image if you just want to try the application on your server or PC. All
the following steps are performed on a debian based linux distribution.
If your setup differs (e.g. in Red Hat based distros the package names are
slightly different) you will need to change the steps as appropriate.

The application is compatible and regularly tested with

* sqlite, postgres
* python 2.7, 3.4, 3.5 and 3.6

You might also want to take a look at the :ref:`other-changes` section for other
changes you might want to do to your local instance such as Terms of Service or
contact page.

.. note::
    Please note that all the steps related to upgrading the database or
    downloading external JS dependencies mentioned in the :ref:`tips` section
    in the development page apply to all the installation options.


These are the necessary packages for both development and production
(node and npm are only used to download JS and CSS libraries)::

    sudo apt-get install nodejs nodejs-legacy npm git \
                         python-virtualenv python3-dev \
                         libjpeg8-dev zlib1g-dev libwebp-dev

On fedora 23::

    sudo dnf install nodejs npm git \
                     python-virtualenv python3-devel \
                     libjpeg-turbo-devel zlib-devel


.. note::
    The application is developed with python 3, which these installation
    instructions also use. If you want to use python 2.7, make sure you install
    the appropriate packages (e.g. python-dev instead of python3-dev, etc.)!


.. toctree::
   :maxdepth: 2

   development
   docker
   production


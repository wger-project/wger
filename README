What is this?
=============

Workout Manager is a free, open source web application that manages your exercises and workouts.
It started as a pet project of mine to replace my growing collection of different spreadsheets, but
it has grown to something other people could also find useful.


What can it do?
---------------

First of all, it is a **workout manager**. That means that you can create and, well, manage your workout
routines. You select how many days you workout constists of, and then add different sets and
exercises to each day. If you do supersets, no worry, it is supported as well and you will know
which exercises "belong together". Each set can have a different number of reps you want to reach
and which you enter yourself. This means that other training forms like pyramid training or
similar are not a problem.

It can also generate a PDF with your current routine. This is suitable for printing so you can bring
it to the gym and keep a log about your progress.

Note: it has no 'preset' workouts that you can simply use (e.g. beginner, etc.). It will happily
make the routine you tell it to do, but you have to decide which exercises and how many repetitions
you'll do.

It also has a **weight module**. This rather simple part basically lets you input your weight and
a day. From this it generates a rather nice looking chart, so you can see if you are reaching your
goals (be it gaining mass or losing it).

In case you want to jump ship after inputing your data from the last years, simply export the
data as CSV.

And finally it is a **nutrition schedule manager**. Here you can create a diet plan and see some
nutritional values (total energy, protein, carbohydrates, and so on) about it. It can also be
downloaded as a PDF so you can keep it on your fridge, so you don't *forget* to follow the plan...
If you install it yourself and add the `ingredients.json` fixture, you will have access to more than
6000 ingredients from the U.S. Department of agriculture.

Note: this is not a log keeper. It does not keep track of what you *actually* ate during the day
and how it compares to what the plan says. It simply shows you the nutritional values of the plan
you create.


Future plans
------------

These are some ideas I have, perhaps I will add them to a future version, perhaps not. If you think
a feature is absolutely missing, don't hesitate to write me an email (see 'Contact_')

* Workout log: do a log of the weight and reps you really did on that exercise. With this data there
  are some nice posibilities like showing your progress over time and other statistics.
* Copy workout and diet plan. Since one workout/plan do not differ that much from the previous one,
  it would be nice to be able to copy the old one and just edit the parts that changed.

Technical details
=================

Sources
-------

All the code and the content is freely available:

* **Main repository**: HG, https://bitbucket.org/rolandgeider/workout_manager
* **Mirror**: GIT, https://github.com/rolandgeider/workout_manager


Installation
------------

This is a Django application, so refer for details to its `installation page`_ if things don't go
as expected or if you are using a different setup.

In short, these are the steps to perform for an installation on a linux machine, with python already
installed. I personally like installing my development files on a virtualenv, it helps keep the
system more or less clean and are very easy to set up. ::

 $ sudo apt-get install python-virtualenv
 $ mkdir manager
 $ cd manager
 $ virtualenv python-django
 $ source python-django/bin/activate
 $ pip install django
 $ pip install reportlab
 $ python
 >>> import django

If the import worked, everything is set up.

Now let's install the application itself ::

 $ hg clone https://rolandgeider@bitbucket.org/rolandgeider/workout_manager
 $ cd workout_manager/workout_manager
 $ mv settings.sample.py settings.py

Edit settings.py, setting the type of database you want to use. The fastest to set up is Sqlite, but
you can use whatever Django supports. Initialise the database and create a super user::

 $ cd ..
 $ python manage.py syncdb

Now you are ready to go, the application is installed and can be used. However, an application like
this without data is not interesting, so you should load some initial data to populate the categories,
etc.

For this, load these fixtures, *in this order*, as some dependend on each other:

* ``python manage.py loaddata languages`` (this is specially important, things depend on the language table)
* ``python manage.py loaddata muscles``
* ``python manage.py loaddata categories``
* ``python manage.py loaddata exercises``
* ``python manage.py loaddata ingredients``

Now, run the server::

$ cd workout_manager
$ python manage.py runserver

You can now access the site with your browser: `http://localhost:8000/`

Compatibility
-------------

The icons used on the site are SVG images and that means that Internet Explorer will only render
them starting with version 9. As expected, all other modern browsers have no problems with this.
The same applies to the SVG backgrounds used, e.g. to show which muscles an exercises works.

While the site uses heavily javascript, it is possible to access almost all the functionality
without it. There are non-javascript fallbacks, the biggest exception to this is the weight chart,
it is generated with javascript and doesn't work without it.


Licence
-------

The application was written using django and is licenced under the Affero GPL 3 or later.

The initial exercise data is licensed additionally under a Creative Commons Attribution Share-Alike
(CC-BY-SA) 3.0

The YAML CSS framework is licensed under a Creative Commons Attribution 2.0 License (CC-BY 2.0)

Some images where taken from Wikipedia, see the SOURCES file in their respective folders for more
details.

Contact
-------

Feel free to write me an email (``roland @ NO!SPAM! geider.net``) if you found this useful or if there
was something that didn't behave as you expected. Alternatively, you can also open a ticket on
the bitbucket tracker: https://bitbucket.org/rolandgeider/workout_manager/issues


.. _installation page: https://docs.djangoproject.com/en/1.4/intro/install/
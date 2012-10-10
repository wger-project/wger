What is this?
=============

Than you for downloading Workout Manager. Workout Manager is a free, open
source web application that manages your exercises, workouts, weight and 
diet plans.

For more details (and screenshots!), refer to the project's wiki:
https://bitbucket.org/rolandgeider/workout_manager/wiki  


Technical details
=================

Sources
-------

All the code and the content is freely available:

* **Main repository**: HG, https://bitbucket.org/rolandgeider/workout_manager
* **Mirror**: GIT, https://github.com/rolandgeider/workout_manager


Contact
-------

Feel free to write me an email (``roland @ NO!SPAM! geider.net``) if you found
this useful or if there was something that didn't behave as you expected.
Alternatively, you can also open a ticket on the bitbucket tracker:
https://bitbucket.org/rolandgeider/workout_manager/issues



Installation
------------

This is a Django application, so if you know how to install one, you can instal
this one. There are more detailed instructions on
https://bitbucket.org/rolandgeider/workout_manager/wiki/Install


Compatibility
-------------

The icons used on the site are SVG images and that means that Internet
Explorer will only render them starting with version 9. As expected, all other
modern browsers have no problems with this. The same applies to the SVG
backgrounds used, e.g. to show which muscles an exercises works.

While the site uses heavily javascript, it is possible to access almost all the
functionality without it. There are non-javascript fallbacks, the biggest
exception to this is the weight chart, it is generated with javascript and
doesn't work without it.


Licence
-------

The application was written using django and is licenced under the Affero GPL 3
or later.

The initial exercise data is licensed additionally under a Creative Commons
Attribution Share-Alike 3.0 (CC-BY-SA 3.0)

The YAML CSS framework is licensed under a Creative Commons Attribution 2.0
License (CC-BY 2.0)

Some images where taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

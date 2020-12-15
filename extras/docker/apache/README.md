Demo image for wger
===================
wger (ˈvɛɡɐ) Workout Manager is a free, open source web application that help
you manage your personal workouts, weight and diet plans and can also be used
as a simple gym management utility. It offers a REST API as well, for easy
integration with other projects and tools.


Please note that this image will overwrite your data when you pull a new version,
it is only intended as an easy to setup demo. If you want to host your own
instance, take a look at the provided docker compose file. That config will
persist your database and uploaded images:

<https://github.com/wger-project/docker>

Installation
------------

This docker image contains an instance of the application running as a WSGI
process under apache with a sqlite database. It is useful to just try it out and
play around. To start it:


```docker run -ti --name wger.apache --publish 8000:80 wger/apache```

Then just open <http://localhost:8000> and log in as: **admin**, password **adminadmin**

To stop the container:

```sudo docker container stop wger.apache```

To start developing again:

```sudo docker container start --attach wger.apache```


Building
--------

If you build this yourself, keep in mind that you **must** build from the
project root!

```docker build -f extras/docker/apache/Dockerfile --tag wger/apache .```


Contact
-------

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* discord: <https://discord.gg/rPWFv6W>
* gitter: <https://gitter.im/wger-project/wger>
* issue tracker: <https://github.com/wger-project/wger/issues>
* twitter: <https://twitter.com/wger_project>

Sources
-------

All the code and the content is freely available:

* Main repository: <https://github.com/wger-project/wger>

Licence
-------

The application is licenced under the Affero GNU General Public License 3 or
later (AGPL 3+).

The initial exercise and ingredient data is licensed additionally under one of
the Creative Commons licenses, see the individual exercises for more details.

The documentation is released under a CC-BY-SA either version 4 of the License,
or (at your option) any later version.

Some images where taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

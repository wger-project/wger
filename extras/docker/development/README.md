# Development image for wger
wger (ˈvɛɡɐ) Workout Manager is a free, open source web application that help
you manage your personal workouts, weight and diet plans and can also be used
as a simple gym management utility. It offers a REST API as well, for easy
integration with other projects and tools.

Please note that this image is intended for development, if you want to
host your own instance, take a look at the provided docker compose file:

<https://github.com/wger-project/docker>



## Usage

This docker image is meant to provide a quick development environment using
django's development server and an sqlite database from your current code
checkout (if you don't want or need a local checkout, use the wger/apache image,
it is self-contained).

A more comfortable development version is provided in the compose folder.

### 1 - Start the container


    docker run -ti  \
       -v /path/to/your/wger/checkout:/home/wger/src \
       --name wger.devel \
       --publish 8000:8000 wger/devel

When developing with windows, you might have problems with the `--volume` option,
use the more verbose mount instead:

    --mount type=bind,source='"C:\your\path\to your\checkout"',target=/home/wger/src

You might also want to download the exercise images and the ingredients
(will take some time):

    docker exec wger.devel python3 manage.py download-exercise-images
    docker exec wger.devel wger load-online-fixtures

### 2 - Open the Application

Just open <http://localhost:8000> and log in as: **admin**, password **adminadmin**

To stop the container:

```sudo docker container stop wger.devel```

To start developing again:

```sudo docker container start --attach wger.devel```

### 3 - Other commands

If you need to update the CSS/JS libraries or just issue some other command:

     docker exec -ti wger.devel yarn
     docker exec -ti wger.devel /bin/bash

## Building

If you build this yourself, keep in mind that you **must** build from the
project root!

```docker build -f extras/docker/development/Dockerfile --tag wger/devel .```


## Contact

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* discord: <https://discord.gg/rPWFv6W>
* gitter: <https://gitter.im/wger-project/wger>
* issue tracker: <https://github.com/wger-project/wger/issues>
* twitter: <https://twitter.com/wger_project>

## Sources

All the code and the content is freely available:

* Main repository: <https://github.com/wger-project/wger>

## Licence

The application is licenced under the Affero GNU General Public License 3 or
later (AGPL 3+).

The initial exercise and ingredient data is licensed additionally under one of
the Creative Commons licenses, see the individual exercises for more details.

The documentation is released under a CC-BY-SA either version 4 of the License,
or (at your option) any later version.

Some images where taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

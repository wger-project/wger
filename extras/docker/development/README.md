# Development image for wger

wger (ˈvɛɡɐ) Workout Manager is a free, open source web application that help
you manage your personal workouts, weight and diet plans and can also be used
as a simple gym management utility. It offers a REST API as well, for easy
integration with other projects and tools.

If you want to host your own instance, take a look at the provided docker compose file:

<https://github.com/wger-project/docker>

## Usage

This docker image is meant to provide a quick development environment using
django's development server and an sqlite database from your current code
checkout (if you don't want or need a local checkout, use the wger/demo image,
it is self-contained).

A more comfortable development version is provided in the compose folder.

### 1 - Installing docker

Install docker, and the docker buildx tool (if they are separate packages on your system, e.g. on Arch Linux)

### 2 - Obtaining/building the docker image

We will run the `wger/server:latest` image in the next step.

You can either download it from [dockerhub](https://hub.docker.com/r/wger/server); docker will do this automatically if you have no such image with that tag yet.
You can also run `docker pull wger/server` to get the latest version. (you can use `docker images` to see if your image is old)

Alternatively, you can build it yourself from your wger code checkout.
To do this, you **must** build from the project root!

```docker build -f extras/docker/development/Dockerfile --tag wger/server .```

### 3 - Start the container

    docker run -ti  \
       -v /path/to/your/wger/checkout:/home/wger/src \
       --name wger.devel \
       --publish 8000:8000 wger/server

When developing with windows, you might have problems with the `--volume` option,
use the more verbose mount instead:

    --mount type=bind,source='"C:\your\path\to your\checkout"',target=/home/wger/src

You might also want to download the exercise images and the ingredients
(will take some time):

    docker exec wger.devel python3 manage.py sync-exercises
    docker exec wger.devel python3 manage.py download-exercise-images
    docker exec wger.devel wger load-online-fixtures

### 4 - Open the Application

Just open <http://localhost:8000> and log in as: **admin**, password **adminadmin**

To stop the container:

```sudo docker container stop wger.devel```

To start developing again:

```sudo docker container start --attach wger.devel```

### 5 - Other commands

If you need to update the CSS/JS libraries or just issue some other command:

     docker exec -ti wger.devel yarn
     docker exec -ti wger.devel /bin/bash

## Contact

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* Discord: <https://discord.gg/rPWFv6W>
* Issue tracker: <https://github.com/wger-project/wger/issues>
* Mastodon: <https://fosstodon.org/@wger>

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

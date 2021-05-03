# Development image for wger

Thank you for downloading wger Workout Manager. wger (ˈvɛɡɐ) is a free, open
source web application that manages your exercises and personal workouts, weight
and diet plans. It can also be used as a simple gym management utility, providing
different administrative roles (trainer, manager, etc.). It offers a REST API
as well, for easy integration with other projects and tools.


## Usage

This docker-compose file starts up a development environment with django's
development server, postgres as a database and redis for caching and saving
the sessions. It binds your current code checkout into the volume, if you
don't want or have one, use the `wger/apache` image, it is self-contained.

### 1 - Start all services

To start all services:

    docker-compose -f extras/docker/compose/docker-compose.yml up

You might also want to download the exercise images and the ingredients
(will take some time):

    docker-compose -f extras/docker/compose/docker-compose.yml exec web wger download-exercise-images
    docker-compose -f extras/docker/compose/docker-compose.yml exec web wger load-online-fixtures

Then open <http://localhost:8000> and log in as: **admin**, password **adminadmin**


### 2 - Lifecycle Management

To stop all services issue a stop command, this will preserve all containers
and volumes:

    docker-compose -f extras/docker/compose/docker-compose.yml stop

To start everything up again:

    docker-compose -f extras/docker/compose/docker-compose.yml start

To remove all containers (except for the postgres volume)

    docker-compose -f extras/docker/compose/docker-compose.yml down

To view the application's log:

    docker-compose -f extras/docker/compose/docker-compose.yml logs -f

### 2 - Other commands

You might need to issue other commands or do other manual work in the container,
e.g.

     docker-compose -f extras/docker/compose/docker-compose.yml exec web yarn install
     docker-compose -f extras/docker/compose/docker-compose.yml exec --user root web /bin/bash

When developing some feature that requires database updates, you might find
if easier to remove the DJANGO_DB_* entries from the dev.env file so that
an sqlite file in ~/db/ is used instead of postgres. Then you can simply copy
the file to re-run migrations, etc.

## Building

If you want to build this yourself, keep in mind that you **must** build from the
project root. Make sure the wger/devel image is available locally as well:

    docker-compose -f extras/docker/compose/docker-compose.yml build.


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

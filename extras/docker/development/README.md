# Development image for wger - Ubuntu based

Thank you for downloading wger Workout Manager. wger (ˈvɛɡɐ) is a free, open
source web application that manages your exercises and personal workouts, weight
and diet plans. It can also be used as a simple gym management utility, providing
different administrative roles (trainer, manager, etc.). It offers a REST API
as well, for easy integration with other projects and tools.


## Usage

This docker image is meant to provide a quick development environment using
django's development server and an sqlite database from your current code
checkout (if you don't want or need a local checkout, use the wger/apache image,
it is self-contained)

### 1 - Start the container


    docker run -ti  \
       -v /path/to/your/wger/checkout:/home/wger/src \
       --name wger.devel \
       --publish 8000:8000 wger/devel

When developing with windows, you might have problems with the `--volume` option,
use the more verbose mount instead:
 
    --mount type=bind,source='"C:\your\path\to your\checkout"',target=/home/wger/src

### 2 - Download additional files

On the first run, you need to download some CSS and JS files with bower (
as well as everytime there are updates):

     docker exec -ti wger.devel python3 manage.py bower install

You might also want to download the exercise images (will take some time):

    docker exec -ti wger.devel python3 manage.py download-exercise-images

### 3 - Open the Application

Just open <http://localhost:8000> and log in as: **admin**, password **admin**

To stop the container:

```sudo docker container stop wger.devel```

To start developing again:

```sudo docker container start --attach wger.devel```


## Building

If you build this yourself, keep in mind that you **must** build from the
project root!

```docker build -f extras/docker/development/Dockerfile --tag wger/devel .```


## Contact

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* gitter: <https://gitter.im/wger-project/wger>
* issue tracker: <https://github.com/wger-project/wger/issues>
* twitter: <https://twitter.com/wger_de>
* mailing list: <https://groups.google.com/group/wger> / wger@googlegroups.com, no registration needed

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

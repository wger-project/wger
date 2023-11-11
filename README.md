# wger
<img src="https://raw.githubusercontent.com/wger-project/wger/master/wger/core/static/images/logos/logo.png" width="100" height="100" />

wger (ˈvɛɡɐ) Workout Manager is a free, open source web application that helps
you manage your personal workouts, weight and diet plans and can also be used
as a simple gym management utility. It offers a REST API as well, for easy
integration with other projects and tools.

For a live system, refer to the project's site: <https://wger.de/>

![Workout plan](https://raw.githubusercontent.com/wger-project/wger/master/wger/software/static/images/workout.png)

## Web app tutorial
First, you will need to create an account with a valid email address and password. Once completed, you will be greeted with the following screen:

![TutorialImage1](wger/core/static/images/tutorialImage3.png)

There are three main sections for users to track their progress: **workout**, **nutrition** and **weight**. On the navigation bar at the top there are options to further explore these categories. Let’s start by exploring the training dropdown:

![TutorialImage2](wger/core/static/images/tutorialImage4.png)

As seen above, there are options to create workout routines that we would like to remember or track, as well as a calendar in which we can see our workout schedule. To create workouts, we can use our own custom templates or public templates created by other users. Feel free to explore the various options.

Moving on to the nutrition tab we can see that we have access to different options:

![TutorialImage3](wger/core/static/images/tutorialImage2.png)

Here we can plan out our nutrition schedule as well as calculate our BMI. There is also the option to check the amount of recommended calories a user should be consuming. In the Ingredient overview section we can check the amount of calories and nutrition information on various common ingredients, which has been uploaded and supplied by other users.

Finally, we move on to the Body Weight dropdown:

![TutorialImage4](wger/core/static/images/tutorialImage1.png)

Weight overview will take us to a time chart which tracks our entered weight fluctuations over time. Add weight entry allows us to update this information with a current entry of weight. Both of these options can be viewed and accessed from the larger ‘Weight’ box on the home page.

This tutorial serves as a guide to get you started exploring the options available in the application. Please feel free to edit and make changes by contributing to the community. Thank you for taking the time to check out wger!


## Mobile app
[<img src="https://play.google.com/intl/en_us/badges/images/generic/en-play-badge.png"
      alt="Get it on Google Play"
      height="80">](https://play.google.com/store/apps/details?id=de.wger.flutter)
[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png"
      alt="Get it on F-Droid"
      height="80">](https://f-droid.org/packages/de.wger.flutter/)


## Installation

These are the basic steps to install and run the application locally on a Linux
system. There are more detailed instructions, other deployment options as well
as an administration guide available at <https://wger.readthedocs.io> or in the
[docs repo](https://github.com/wger-project/docs).

Please consult the commands' help for further information and available
parameters.


### Production

If you want to host your own instance, take a look at the provided docker
compose file. This config will persist your database and uploaded images:

<https://github.com/wger-project/docker>

### Demo

If you just want to try it out:

```shell script
    docker run -ti --name wger.demo --publish 8000:80 wger/demo
```

Then just open <http://localhost:8000> and log in as **admin**, password **adminadmin**

Please note that this image will overwrite your data when you pull a new version,
it is only intended as an easy to setup demo

### Development version

We provide a docker file that sets everything up for development (however this won't
persist any data)

````shell script
docker run -ti  \
    -v /path/to/your/wger/checkout:/home/wger/src \
    --name wger.dev \
    --publish 8000:8000 \ 
    wger/server
````

Then just open <http://localhost:8000> and log in as: **admin**, password **adminadmin**

For more info, check the [README in wger/extras/developemt](
 ./extras/docker/development/README.md
).

Alternatively you can use the production compose file for development as well,
just bind your local source code into the web container (see the docker-compose.yml
file for details). You will also probably want to set `DJANGO_DEBUG to false

#### Local installation

If you prefer a local installation, consult the
[development documentation](https://wger.readthedocs.io/en/latest/development.html)


## Contact

Feel free to contact us if you found this useful or if there was something that
didn't behave as you expected. We can't fix what we don't know about, so please
report liberally. If you're not sure if something is a bug or not, feel free to
file a bug anyway.

* **discord:** <https://discord.gg/rPWFv6W>
* **issue tracker:** <https://github.com/wger-project/wger/issues>
* **twitter:** <https://twitter.com/wger_project>


## Sources

All the code and the content is available on github:

<https://github.com/wger-project/wger>


## Translation
Translate the app to your language on [Weblate](https://hosted.weblate.org/engage/wger/).

[![translation status](https://hosted.weblate.org/widgets/wger/-/multi-blue.svg)](https://hosted.weblate.org/engage/wger/)


## License

The application is licensed under the Affero GNU General Public License 3 or
later (AGPL 3+).

The initial exercise and ingredient data is licensed additionally under one of
the Creative Commons licenses, see the individual exercises for more details.

The documentation is released under a CC-BY-SA: either version 4 of the License,
or (at your option) any later version.

Some images were taken from Wikipedia, see the SOURCES file in their respective
folders for more details.

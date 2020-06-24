#
# Docker image for wger development
#
# Please consult the documentation for usage
#
# Note: you MUST build this image from the projec's root!
# docker build -f extras/docker/development/Dockerfile --tag wger/devel .
#
# Run the container:
# docker run -ti --publish 8000:8000 --name wger.devel  wger/devel
# (in docker) source ~/venv/bin/activate
# (in docker) python manage.py download-exercise-images (optional, may take some time)
# (in docker) python manage.py runserver 0.0.0.0:8000
#
# Alternatively, you can bind the local checkout into the container:
# docker run -ti -v /path/to/this/checkout:/home/wger/src --name wger.devel --publish 8000:8000 wger/devel
#
#
# To stop the container:
# sudo docker container stop wger.devel
#
# To start developing again
# sudo docker container start --attach wger.devel
#

FROM wger/base:1.9

LABEL maintainer="Roland Geider <roland@geider.net>"
EXPOSE 8000

# Set locale to UTF8, otherwise problems with the encoding can occur, e.g.
# when using the invoke/wger commands and bower
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Path to where misc docker files live, relative to the project root
ARG DOCKER_DIR=./extras/docker/development

# Set up the application
USER wger
COPY --chown=wger:wger . /home/wger/src
#RUN git clone https://github.com/wger-project/wger.git /home/wger/src

WORKDIR /home/wger/src
RUN python3 -m venv /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install wheel \
    && pip install -r requirements_devel.txt \
    && pip install -r requirements_forked.txt \
    && python setup.py develop \
    && npm install \
    && npm install bower \
    && wger create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
        --settings-path /home/wger/src/settings.py \
        --no-start-server

# Download the exercise images
RUN mkdir ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && . /home/wger/venv/bin/activate


USER root
RUN apt-get remove -y \
        build-essential  \
        python-dev \
    && apt autoremove -y

USER wger
CMD ["/bin/bash"]

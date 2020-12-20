#
# Docker image for wger development:
#
# This image uses a virtual environment, which is not necessary in a docker
# image and is more or less intended to check that the installation instructions
# for a local development are up-to-date
#
# Please consult the documentation for usage
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/development/Dockerfile --tag wger/devel .
#
# Run the container:
# docker run -ti --publish 8000:8000 --name wger.devel  wger/devel
# (in docker) source ~/venv/bin/activate
# (in docker) python manage.py download-exercise-images (optional, may take some time)
# (in docker) wger load-online-fixtures (optional, may take some time)
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

##########
# Builder
##########
FROM ubuntu:20.04 as builder

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
      build-essential \
      python3-dev \
      python3-pip \
      git \
  && rm -rf /var/lib/apt/lists/*

# Set up the application
COPY . .
RUN pip3 install wheel \
    && pip3 wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements_dev.txt


########
# Final
########
FROM wger/base:2.0-dev
LABEL maintainer="Roland Geider <roland@geider.net>"
ARG DOCKER_DIR=./extras/docker/development
EXPOSE 8000

# Set up the application
USER wger
COPY --chown=wger:wger . /home/wger/src
COPY --from=builder /usr/src/app/wheels /wheels
#RUN git clone https://github.com/wger-project/wger.git /home/wger/src

WORKDIR /home/wger/src
RUN python3 -m venv /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache /wheels/* \
    && python setup.py develop \
    && wger create-settings --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
    && wger load-online-fixtures

# Download the exercise images
RUN mkdir ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py

CMD ["/bin/bash"]

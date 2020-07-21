#
# Docker image for wger development
#
# Please consult the documentation for usage
#
# Note: you MUST build this image from the projec's root!
# docker build -f extras/docker/development/Dockerfile --tag wger/devel .
#
# Run the container:
# docker run -ti -v /path/to/this/checkout:/home/wger/src --name wger.devel --publish 8000:8000 wger/devel
#
# (in docker) python3 manage.py download-exercise-images (optional, may take some time)
# (in docker) python3 manage.py runserver 0.0.0.0:8000
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
      python3-wheel \
      git \
  && rm -rf /var/lib/apt/lists/*

# Build the necessary python wheels
COPY requirements* ./
RUN pip3 wheel --no-cache-dir --wheel-dir /wheels -r requirements_devel.txt



########
# Final
########
FROM wger/base:2.0-dev
LABEL maintainer="Roland Geider <roland@geider.net>"
ARG DOCKER_DIR=./extras/docker/development
EXPOSE 8000

# Set locale to UTF8, otherwise problems with the encoding can occur, e.g.
# when using the invoke/wger commands and bower
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Set up the application
WORKDIR /home/wger/src
COPY --chown=wger:wger . /home/wger/src
COPY --from=builder /wheels /wheels
COPY ${DOCKER_DIR}/settings.py /home/wger/src
COPY ${DOCKER_DIR}/entrypoint.sh /home/wger/entrypoint.sh
RUN chmod +x /home/wger/entrypoint.sh
RUN pip3 install --no-cache /wheels/* \
    && pip3 install psycopg2-binary \
    && pip3 install python-memcached \
    && python3 setup.py develop \
    && npm install \
    && npm install bower

RUN chown -R wger:wger .
USER wger
RUN mkdir ~/media
RUN mkdir ~/db/

CMD ["/home/wger/entrypoint.sh"]

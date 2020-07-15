#
# A wger installation under apache with WSGI
#
# Note: you MUST build this image from the projec's root!
# docker build -f extras/docker/apache/Dockerfile --tag wger/apache .
#
# Please consult the documentation for usage
# docker build --tag wger/apache .
# docker run -ti --name wger.apache --publish 8000:80 wger/apache
#
# To stop the container:
# sudo docker container stop wger.apache
#
# To start developing again
# sudo docker container start --attach wger.apache
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
    && pip3 wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements_devel.txt


########
# Final
########
FROM wger/base:1.9

LABEL maintainer="Roland Geider <roland@geider.net>"
ARG DOCKER_DIR=./extras/docker/apache
EXPOSE 80

# Set locale to UTF8, otherwise problems with the encoding can occur, e.g.
# when using the invoke/wger commands and bower
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


# Install dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    apache2 \
    cron \
    libapache2-mod-wsgi-py3 \
  && rm -rf /var/lib/apt/lists/*

# Configure apache
COPY ${DOCKER_DIR}/wger.conf /etc/apache2/sites-available/
RUN a2dissite 000-default.conf \
  && a2enmod headers \
  && a2ensite wger \
  && echo "ServerName localhost" >> /etc/apache2/conf-available/fqdn.conf \
  && a2enconf fqdn \
  && usermod -G wger www-data

# Configure cron
COPY ${DOCKER_DIR}/crontab /etc/cron.d/wger
COPY ${DOCKER_DIR}/venvwrapper /home/wger/venvwrapper
COPY ${DOCKER_DIR}/entrypoint.sh /home/wger/entrypoint.sh

RUN chmod 0644 /etc/cron.d/wger \
  && chmod +x /home/wger/venvwrapper /home/wger/entrypoint.sh \
  && touch /var/log/cron.log

COPY --chown=wger:www-data . /home/wger/src
COPY --from=builder /usr/src/app/wheels /wheels

# Set up the application
RUN ln -s /home/wger/static/CACHE /var/www
USER wger

WORKDIR /home/wger/src
RUN python3 -m venv /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install wheel \
    && pip install --no-cache /wheels/* \
    && python setup.py develop \
    && npm install \
    && npm install bower \
    && wger create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
        --settings-path /home/wger/src/settings.py \
        --no-start-server


# Change permissions of some files and folders so the apache process
# can access them.
RUN mkdir -p ~/static/CACHE ~/media \
    && ln -s /home/wger/static/CACHE /home/wger/src/CACHE \
    && chmod g+w /home/wger/static/CACHE \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py

USER root
RUN apt-get remove build-essential -y \
    && apt autoremove -y \
    && chown www-data:www-data -R /home/wger/db

ENTRYPOINT ["/home/wger/entrypoint.sh"]

#
# A wger installation under apache with WSGI
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/demo/Dockerfile --tag wger/demo .
#
# Please consult the documentation for usage
# docker run -ti --name wger.demo --publish 8000:80 wger/demo
#
# To stop the container:
# sudo docker container stop wger.demo
#
# To start again
# sudo docker container start --attach wger.demo
#

##########
# Builder
##########
FROM wger/base:latest as builder
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update \
  && apt install --no-install-recommends -y \
      build-essential \
      python3-dev \
      python3-wheel \
      pkg-config \
      libcairo2-dev \
      libjpeg8-dev \
      libwebp-dev \
      libpq-dev \
      rustc \
      cargo \
  && pip install --upgrade pip

# Build the necessary python wheels
# Note that the --mount is a workaround for https://github.com/rust-lang/cargo/issues/8719
COPY requirements* ./
RUN --mount=type=tmpfs,target=/root/.cargo pip3 wheel --no-cache-dir --wheel-dir /wheels -r requirements_docker.txt


########
# Final
########
FROM wger/base:latest
LABEL maintainer="Roland Geider <roland@geider.net>"

ARG DOCKER_DIR=./extras/docker/demo
EXPOSE 80


# Install dependencies
RUN apt-get install --no-install-recommends -y \
    apache2 \
    cron \
    python3-venv \
    libapache2-mod-wsgi-py3 \
    python3-wheel

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

COPY --from=builder /wheels /wheels
COPY --chown=wger:www-data . /home/wger/src

# Set up the application
RUN ln -s /home/wger/static/CACHE /var/www
USER wger

WORKDIR /home/wger/src
#RUN git clone https://github.com/wger-project/wger.git
RUN python3 -m venv /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache /wheels/* \
    && pip install -e . \
    && wger create-settings --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
    && wger load-online-fixtures \
    && python3 manage.py sync-exercises \
    && python3 manage.py download-exercise-images


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
    && chown :www-data -R /home/wger/db \
    && chmod g+w /home/wger/db /home/wger/db/database.sqlite

ENTRYPOINT ["/home/wger/entrypoint.sh"]

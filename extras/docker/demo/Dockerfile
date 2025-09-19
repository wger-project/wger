#
# A demo wger installation under apache with WSGI
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/demo/Dockerfile --tag wger/demo .
#
# Please consult the documentation for usage
# docker run --rm --name wger.demo --publish 8000:80 wger/demo
#
# To stop the container:
# docker container stop wger.demo
#
# To start again
# docker container start --attach wger.demo
#

##########
# Builder
##########
FROM wger/base:latest AS builder
ARG DEBIAN_FRONTEND=noninteractive

RUN wget -O- https://deb.nodesource.com/setup_22.x | bash - \
  && apt update \
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
      sassc \
      nodejs \
    && ln -s /usr/bin/sassc /usr/bin/sass \
    && rm -rf /var/lib/apt/lists/* \
    && corepack enable

# Build the necessary python wheels
# Note that the --mount is a workaround for https://github.com/rust-lang/cargo/issues/8719
WORKDIR /home/wger/src

COPY pyproject.toml /home/wger/src
COPY wger/version.py /home/wger/src/wger/
COPY wger/__init__.py /home/wger/src/wger/
COPY README.md /home/wger/src
COPY package.json /home/wger/src
COPY yarn.lock /home/wger/src
COPY wger/core/static /home/wger/src/wger/core/static
RUN --mount=type=tmpfs,target=/root/.cargo pip3 wheel --no-cache-dir --wheel-dir /wheels --group docker . \
  && yarn install \
  && yarn build:css:sass


########
# Final
########
FROM wger/base:latest AS final
LABEL org.opencontainers.image.authors="wger team <hello@wger.de>"
ENV TERM=xterm
ARG DOCKER_DIR=./extras/docker/demo
EXPOSE 80


# Install dependencies
RUN apt update \
    && apt install --no-install-recommends -y \
        apache2 \
        cron \
        python3-venv \
        libapache2-mod-wsgi-py3 \
        python3-wheel \
    && apt-get clean \
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

RUN chmod 0644 /etc/cron.d/wger \
  && chmod +x /home/wger/venvwrapper \
  && touch /var/log/cron.log

COPY --chown=wger:www-data . /home/wger/src
COPY --from=builder --chown=wger:wger /home/wger/src/wger/core/static/yarn /home/wger/src/wger/core/static/yarn

# Set up the application
RUN ln -s /home/wger/static/CACHE /var/www
USER wger

WORKDIR /home/wger/src
RUN python3 -m venv /home/wger/venv

# Change permissions of some files and folders so the apache process
# can access them.
RUN mkdir -p ~/static/CACHE ~/media \
    && ln -s /home/wger/static/CACHE /home/wger/src/CACHE \
    && chmod g+w /home/wger/static/CACHE

RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels  . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache /wheels/* \
    && pip install -e . \
    && wger create-settings --database-path /home/wger/db/database.sqlite \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py \
    && wger bootstrap --no-process-static \
    && python3 manage.py sync-exercises \
    && wger load-online-fixtures \
    && python3 manage.py download-exercise-images \
    && python3 manage.py collectstatic --no-input


USER root
RUN chown :www-data -R /home/wger/db \
    && chown www-data:www-data -R /home/wger/static \
    && chmod g+w /home/wger/db /home/wger/db/database.sqlite

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]

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
      nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g sass

# Build the necessary python wheels
WORKDIR /home/wger/src
COPY README.md pyproject.toml package.json package-lock.json package-lock.json /home/wger/src/
COPY wger/version.py wger/__init__.py /home/wger/src/wger/
COPY wger/core/static /home/wger/src/wger/core/static
RUN npm ci --production \
    && npm run build:css:sass \
    && PACKAGE_NAME="@wger-project/react-components" \
    && PACKAGE_VERSION=$(node -p "require('./package.json').devDependencies['$PACKAGE_NAME']") \
    && TARBALL=$(npm pack ${PACKAGE_NAME}@${PACKAGE_VERSION}) \
    && mkdir -p node_modules/${PACKAGE_NAME} \
    && tar -xzf ${TARBALL} -C node_modules/${PACKAGE_NAME} --strip-components=1 \
    && pip3 wheel \
      --no-cache-dir \
      --wheel-dir /wheels \
      --group docker .

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
COPY --chown=wger:wger --from=builder /home/wger/src/node_modules /home/wger/src/node_modules
COPY --chown=wger:wger --from=builder /home/wger/src/wger/core/static/bootstrap-compiled.css /home/wger/src/wger/core/static/bootstrap-compiled.css
COPY --chown=wger:wger --from=builder /home/wger/src/wger/core/static/bootstrap-compiled.css.map /home/wger/src/wger/core/static/bootstrap-compiled.css.map

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
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings/production.py \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings/production.py \
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

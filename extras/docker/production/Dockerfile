#
# Docker image for wger
#
# Please consult the README for usage
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/production/Dockerfile --tag wger/server .
#
# To run the container consult https://github.com/wger-project/docker

##########
# Builder
##########
FROM wger/base:latest AS builder
ARG DEBIAN_FRONTEND=noninteractive

# Need a newer node than what's in ubuntu
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
      unzip \
      nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /root/src/wger/core/static


#
# Build the python wheels
#
WORKDIR /root/src

# Build the application
COPY pyproject.toml README.md /root/src/
COPY wger/version.py wger/__init__.py /root/src/wger/

# NB: this was a workound for https://github.com/rust-lang/cargo/issues/8719
# which was needed when building rust dependencies for arm/v7. If we re-enable
# the arch, we will probably need to add it again (same for demo, etc).
# --mount=type=tmpfs,target=/root/.cargo
RUN pip3 wheel \
      --no-cache-dir \
      --wheel-dir /wheels \
      --group docker . \
    && npm install -g sass

# Fetch the JS and CSS files.
# For the react-components npm package, we fetch it manually, extract it and move
# it into node_modules to keep the size of the docker image small(er). Yes, this
# is hacky and there's probably a better way.
COPY package.json package-lock.json ./
COPY wger/core/static /root/src/wger/core/static
RUN npm ci --production \
    && npm run build:css:sass \
    && PACKAGE_NAME="@wger-project/react-components" \
    && PACKAGE_VERSION=$(node -p "require('./package.json').devDependencies['$PACKAGE_NAME']") \
    && TARBALL=$(npm pack ${PACKAGE_NAME}@${PACKAGE_VERSION}) \
    && mkdir -p node_modules/${PACKAGE_NAME} \
    && tar -xzf ${TARBALL} -C node_modules/${PACKAGE_NAME} --strip-components=1

########
# Final
########
FROM wger/base:latest AS final
LABEL org.opencontainers.image.authors="wger team <hello@wger.de>"
ARG DOCKER_DIR=./extras/docker/production
ARG BUILD_COMMIT
ARG BUILD_DATE

ENV PATH="/home/wger/.local/bin:$PATH"
ENV APP_BUILD_COMMIT=$BUILD_COMMIT
ENV APP_BUILD_DATE=$BUILD_DATE
ENV DJANGO_SETTINGS_MODULE='settings.main'

WORKDIR /home/wger/src
EXPOSE 8000

# Set up the application
COPY --chown=wger:wger . /home/wger/src
COPY --chown=wger:wger --from=builder /root/src/node_modules /home/wger/src/node_modules
COPY --chown=wger:wger --from=builder /root/src/wger/core/static/bootstrap-compiled.css /home/wger/src/wger/core/static/bootstrap-compiled.css
COPY --chown=wger:wger --from=builder /root/src/wger/core/static/bootstrap-compiled.css.map /home/wger/src/wger/core/static/bootstrap-compiled.css.map
COPY ${DOCKER_DIR}/entrypoint.sh /home/wger/entrypoint.sh
COPY ${DOCKER_DIR}/celery/start-beat /start-beat
COPY ${DOCKER_DIR}/celery/start-worker /start-worker
COPY ${DOCKER_DIR}/celery/start-flower /start-flower
RUN chmod +x /home/wger/entrypoint.sh \
    && chmod +x /start-beat \
    && chmod +x /start-worker \
    && chmod +x /start-flower \
    && chown wger:wger /home/wger/src

USER wger
RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    pip3 install --break-system-packages --no-cache-dir --user /wheels/* \
    && pip3 install --break-system-packages --user . \
    && mkdir -p ~/media ~/static ~/beat ~/db \
    && cd wger \
    && django-admin compilemessages

CMD ["/home/wger/entrypoint.sh"]

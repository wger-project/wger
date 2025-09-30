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
      sassc \
      cargo \
      unzip \
      nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && corepack enable \
    && mkdir -p /root/src/wger/core/static


#
# Build the python wheels
#
WORKDIR /root/src

# Build the application
COPY pyproject.toml /root/src
COPY wger/version.py /root/src/wger/
COPY wger/__init__.py /root/src/wger/
COPY README.md /root/src

# NB: the --mount tmpfs is a workaround for https://github.com/rust-lang/cargo/issues/8719
RUN --mount=type=tmpfs,target=/root/.cargo \
    pip3 wheel \
      --no-cache-dir \
      --wheel-dir /wheels \
      --group docker . \
    && ln -s /usr/bin/sassc /usr/bin/sass

# Build the JS and CSS files
COPY package.json yarn.lock .yarnrc.yml ./
COPY wger/core/static /root/src/wger/core/static
RUN yarn install \
    && yarn build:css:sass \
    && cd .. \
    && wget https://github.com/wger-project/react/archive/refs/heads/master.zip \
    && unzip master.zip \
    && cd react-master \
    && yarn config set --home enableTelemetry 0 \
    && yarn config set nodeLinker node-modules \
    && yarn install \
    && WGER_STATIC_FOLDER="/root/src/wger/core/static/react" yarn build


########
# Final
########
FROM wger/base:latest AS final
LABEL org.opencontainers.image.authors="wger team <hello@wger.de>"
ARG DOCKER_DIR=./extras/docker/production
ENV PATH="/home/wger/.local/bin:$PATH"
WORKDIR /home/wger/src
EXPOSE 8000

# Set up the application
COPY --chown=wger:wger . /home/wger/src
COPY --chown=wger:wger --from=builder /root/src/wger/core/static/yarn /home/wger/src/wger/core/static/yarn
COPY --chown=wger:wger --from=builder /root/src/wger/core/static/react /home/wger/src/wger/core/static/react
COPY ${DOCKER_DIR}/settings.py /home/wger/src
COPY ${DOCKER_DIR}/settings.py /tmp/
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

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
      yarnpkg \
      sassc \
      cargo

# Build the necessary python wheels
# Note that the --mount tmpfs is a workaround for https://github.com/rust-lang/cargo/issues/8719
COPY requirements* ./
RUN --mount=type=tmpfs,target=/root/.cargo \
    pip3 wheel --no-cache-dir --wheel-dir /wheels -r requirements_docker.txt \
    && pip3 install --break-system-packages --user --no-cache-dir /wheels/*

# Download and copy js and css files
COPY . /home/wger/src
WORKDIR /home/wger/src
RUN ln -s /usr/bin/yarnpkg /usr/bin/yarn \
    && ln -s /usr/bin/sassc /usr/bin/sass \
    && yarn install \
    && yarn build:css:sass


########
# Final
########
FROM wger/base:latest
LABEL maintainer="Roland Geider <roland@geider.net>"
ARG DOCKER_DIR=./extras/docker/production
ENV PATH="/home/wger/.local/bin:$PATH"

EXPOSE 8000


# Set up the application
WORKDIR /home/wger/src
COPY --chown=wger:wger . /home/wger/src
COPY --from=builder --chown=wger:wger /root/.local /home/wger/.local
COPY --from=builder --chown=wger:wger /home/wger/src/wger/core/static/yarn /home/wger/src/wger/core/static/yarn
COPY ${DOCKER_DIR}/settings.py /home/wger/src
COPY ${DOCKER_DIR}/settings.py /tmp/
COPY ${DOCKER_DIR}/entrypoint.sh /home/wger/entrypoint.sh
COPY ${DOCKER_DIR}/celery/start-beat /start-beat
COPY ${DOCKER_DIR}/celery/start-worker /start-worker
COPY ${DOCKER_DIR}/celery/start-flower /start-flower
RUN chmod +x /home/wger/entrypoint.sh \
    && chmod +x /start-beat \
    && chmod +x /start-worker \
    && chmod +x /start-flower

USER wger
RUN pip3 install --break-system-packages --user -e . \
    && mkdir ~/media \
    && mkdir ~/static \
    && mkdir ~/beat \
    && mkdir ~/db

CMD ["/home/wger/entrypoint.sh"]

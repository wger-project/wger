#
# Docker image for wger development
#
# Please consult the README for usage
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/development/Dockerfile --tag wger/server .
#
# Run the container:
# docker run -ti -v /path/to/this/checkout:/home/wger/src --name wger.dev --publish 8000:8000 wger/server

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
# Note that the --mount tmpfs is a workaround for https://github.com/rust-lang/cargo/issues/8719
COPY requirements* .
RUN --mount=type=tmpfs,target=/root/.cargo \
    pip3 wheel --no-cache-dir --wheel-dir /wheels -r requirements_docker.txt



########
# Final
########
FROM wger/base:latest
LABEL maintainer="Roland Geider <roland@geider.net>"
ARG DOCKER_DIR=./extras/docker/development
ENV PATH="/home/wger/.local/bin:$PATH"

EXPOSE 8000


# Set up the application
WORKDIR /home/wger/src
COPY --chown=wger:wger . /home/wger/src
COPY --from=builder /wheels /wheels
COPY ${DOCKER_DIR}/settings.py /home/wger/src
COPY ${DOCKER_DIR}/settings.py /tmp/
COPY ${DOCKER_DIR}/entrypoint.sh /home/wger/entrypoint.sh
COPY ${DOCKER_DIR}/celery/beat/start /start-beat
COPY ${DOCKER_DIR}/celery/worker/start /start-worker
COPY ${DOCKER_DIR}/celery/flower/start /start-flower
RUN chmod +x /home/wger/entrypoint.sh \
    && chmod +x /start-beat \
    && chmod +x /start-worker \
    && chmod +x /start-flower \
    && pip3 install --no-cache /wheels/* \
    && chown -R wger:wger .

USER wger
RUN pip3 install -e . \
    && mkdir ~/media \
    && mkdir ~/static \
    && mkdir ~/beat \
    && mkdir ~/db/

CMD ["/home/wger/entrypoint.sh"]

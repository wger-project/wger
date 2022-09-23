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
FROM ubuntu:22.04 as builder
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
      build-essential \
      python3-dev \
      python3-pip \
      python3-wheel \
      git

# Build the necessary python wheels
COPY requirements* ./
RUN pip3 wheel --no-cache-dir --wheel-dir /wheels -r requirements_prod.txt



########
# Final
########
FROM wger/base:2.1-dev
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
RUN chmod +x /home/wger/entrypoint.sh
RUN pip3 install --no-cache /wheels/*

RUN chown -R wger:wger .

USER wger
RUN mkdir ~/media \
    && pip3 install -e . \
    && mkdir ~/static \
    && mkdir ~/db/

CMD ["/home/wger/entrypoint.sh"]

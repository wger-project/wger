#
# Base Docker image for wger images
#
#
# This dockerfile simply installs all common dependencies for the
# other images and does not do anything on its own.
#
# docker build --tag wger/base .
#

FROM ubuntu:18.10

LABEL maintainer="Roland Geider <roland@geider.net>"

# Install dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
      git \
      libjpeg8-dev \
      libwebp-dev \
      nodejs \
      nodejs-legacy \
      npm \
      python-virtualenv \
      python3-dev \
      sudo \
      zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*


# Add wger user
RUN adduser wger --disabled-password --gecos ""
RUN echo "wger ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/wger

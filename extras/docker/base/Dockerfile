#
# Base Docker image for wger images
#
#
# This dockerfile simply installs all common dependencies for the
# other images and does not do anything on its own.
#
# docker build --tag wger/base .
#

FROM ubuntu:20.04

LABEL maintainer="Roland Geider <roland@geider.net>"

# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
      git \
      locales \
      nodejs \
      npm \
      python3-venv \
      vim \
      tmux \
      sqlite3 \
  && rm -rf /var/lib/apt/lists/*


# Add wger user
RUN adduser wger --disabled-password --gecos ""

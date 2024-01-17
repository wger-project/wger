#
# Base Docker image for wger images
#
#
# This dockerfile simply installs all common dependencies for the
# other images and does not do anything on its own.
#
# docker build --tag wger/base .
#

FROM ubuntu:22.04

LABEL maintainer="Roland Geider <roland@geider.net>"

# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
  && apt install --no-install-recommends -y \
      locales \
      nodejs \
      npm \
      python3-pip \
      sqlite3 \
      wget \
      tzdata \
      libpq5 \
  && npm install -g yarn sass\
  && locale-gen en_US.UTF-8

# Environmental variables
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Add wger user
RUN adduser wger --disabled-password --gecos ""

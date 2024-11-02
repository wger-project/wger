#
# Base Docker image for wger images
#
#
# This dockerfile simply installs all common dependencies for the
# other images and does not do anything on its own.
#
# docker build --tag wger/base .
#

FROM ubuntu:24.04

LABEL maintainer="Roland Geider <roland@geider.net>"

# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
  && apt install --no-install-recommends -y \
      adduser \
      locales \
      python3-pip \
      sqlite3 \
      wget \
      tzdata \
      libpq5 \
  && locale-gen en_US.UTF-8

# Environmental variables
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Add wger user
RUN deluser ubuntu
RUN adduser wger --uid 1000 --disabled-password --gecos ""

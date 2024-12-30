#
# Installs some additional packages needed for development
#
# Note that this dockerfile is built from the corresponding docker-compose file
#

FROM wger/server:latest

USER root

WORKDIR /home/wger/src
RUN apt-get update && \
    apt-get install -y \
        git \
        vim \
        yarnpkg \
        sassc

COPY ../../../requirements.txt /tmp/requirements.txt
COPY ../../../requirements_dev.txt /tmp/requirements_dev.txt

RUN ln -s /usr/bin/yarnpkg /usr/bin/yarn \
    && ln -s /usr/bin/sassc /usr/bin/sass

USER wger
RUN pip3 install --break-system-packages --user -r /tmp/requirements.txt \
    && pip3 install --break-system-packages --user -r /tmp/requirements_dev.txt

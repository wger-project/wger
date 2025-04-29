#
# Docker file for the development environment
#
# Please consult https://wger.readthedocs.io/en/latest/development/backend.html
# on how to use and start it.

FROM wger/server:latest

USER root

WORKDIR /home/wger/src
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        git \
        vim \
        yarnpkg \
        sassc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/yarnpkg /usr/bin/yarn \
    && ln -s /usr/bin/sassc /usr/bin/sass

USER wger
COPY --chown=wger:wger . /home/wger/src
RUN yarn install \
    && yarn build:css:sass \
    && pip3 install --break-system-packages --user --group dev --editable .

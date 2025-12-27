#
# Docker file for the development environment
#
# Please consult https://wger.readthedocs.io/en/latest/development/backend.html
# on how to use and start it.

FROM wger/server:latest

USER root

WORKDIR /home/wger/src
RUN wget -O- https://deb.nodesource.com/setup_22.x | bash - && \
    apt update && \
    apt install --no-install-recommends -y \
        git \
        vim \
        nodejs \
        sassc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/sassc /usr/bin/sass

USER wger
COPY --chown=wger:wger . /home/wger/src
RUN npm install \
    && npm run build:css:sass \
    && pip3 install --break-system-packages --user --group dev --editable .

#
# Docker image for wger development
#
# Please consult the documentation for usage
# docker build -t wger/devel .
# docker run -ti --name wger.devel --publish 8000:8000 wger/devel
# (in docker) source ~/venv/bin/activate
# (in docker) python manage.py runserver 0.0.0.0:8000
#
#


FROM wger/base

MAINTAINER Roland Geider <roland@geider.net>
EXPOSE 8000

# Install dependencies
RUN apt-get install -y vim tmux sqlite3

# Set up the application
USER wger
RUN git clone https://github.com/wger-project/wger.git /home/wger/src

WORKDIR /home/wger/src
RUN virtualenv --python python3 /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements_devel.txt \
    && invoke create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && invoke bootstrap_wger \
        --settings-path /home/wger/src/settings.py \
        --no-start-server

# Install node modules for JS linting and download the exercise images
#
# Note: it seems there are problems with node and docker, so it's necessary
#       to delete the node_modules folder and install everything again
#       -> https://github.com/npm/npm/issues/9863
#       -> https://github.com/npm/npm/issues/13306
RUN rm -r node_modules \
    && npm install bower \
    && npm install \
    && mkdir ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && . /home/wger/venv/bin/activate \
    && python manage.py download-exercise-images


CMD ["/bin/bash"]

#
# Dockerimage for wger development
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
RUN apt-get install -y vim

# Set up the application
USER wger
RUN git clone https://github.com/rolandgeider/wger.git /home/wger/src
WORKDIR /home/wger/src
RUN virtualenv --python python3 /home/wger/venv
RUN npm install bower \
    && . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements_devel.txt \
    && invoke create_settings \
        --settings-path /home/wger/src/settings.py \
	    --database-path /home/wger/db/database.sqlite \
    && invoke bootstrap_wger --settings-path /home/wger/src/settings.py --no-start-server


CMD ["/bin/bash"]

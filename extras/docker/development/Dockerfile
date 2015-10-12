#
# Dockerimage for wger development
#
# Please consult the documentation for usage
#
#


FROM ubuntu:15.04

MAINTAINER Roland Geider <roland@geider.net>
EXPOSE 8000

RUN apt-get update;\
    apt-get install -y nodejs nodejs-legacy npm git \
        python-virtualenv python3-dev \
        libjpeg8-dev zlib1g-dev libwebp-dev \
	vim

RUN adduser wger --disabled-password --gecos ""
USER wger
RUN git clone https://github.com/rolandgeider/wger.git /home/wger/src
RUN virtualenv --python python3 /home/wger/venv

WORKDIR /home/wger/src
RUN npm install bower \
    && . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements_devel.txt \
    && invoke create_settings \
         --settings-path /home/wger/src/settings.py \
	 --database-path /home/wger/db/database.sqlite \
    && invoke bootstrap_wger --settings-path /home/wger/src/settings.py --no-start-server


CMD ["/bin/bash"]

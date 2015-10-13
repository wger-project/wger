#
# Dockerimage for wger development
#
# Please consult the documentation for usage
# docker build --tag wger/apache .
# docker run -ti --name wger.apache --publish 8000:80 wger/apache
#
#

FROM ubuntu:15.04

MAINTAINER Roland Geider <roland@geider.net>
EXPOSE 80

# Install dependencies
RUN apt-get update;\
    apt-get install -y apache2 libapache2-mod-wsgi-py3 \
        nodejs nodejs-legacy npm git \
        python-virtualenv python3-dev \
        libjpeg8-dev zlib1g-dev libwebp-dev \
	    sudo vim

# Add wger user
RUN adduser wger --disabled-password --gecos ""
RUN echo "wger ALL=(ALL) NOPASSWD:ALL" > etc/sudoers.d/wger

# Configure apache
RUN a2dissite 000-default.conf
ADD wger.conf /etc/apache2/sites-available/
RUN a2ensite wger

# Set up the application
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

# Change permissions of some files and folders so the apache process
# can access them.
RUN chmod o+w -R ~/db/ \
    && . /home/wger/venv/bin/activate \
    && mkdir ~/static \
    && mkdir ~/media \
    && chmod o+w ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py \
    && mkdir /home/wger/src/components \
    && python manage.py collectstatic --noinput

USER root
RUN chmod 755 /usr/sbin/apache2ctl

ENTRYPOINT ["/usr/sbin/apache2ctl"]
CMD ["-D", "FOREGROUND"]
#
# A wger installation under apache with WSGI
#
# Please consult the documentation for usage
# docker build --tag wger/apache .
# docker run -ti --name wger.apache --publish 8000:80 wger/apache
#
#

FROM wger/base

MAINTAINER Roland Geider <roland@geider.net>
EXPOSE 80

# Install dependencies
RUN apt-get install -y apache2 libapache2-mod-wsgi-py3

# Configure apache
RUN a2dissite 000-default.conf
ADD wger.conf /etc/apache2/sites-available/
RUN a2ensite wger

# Set up the application
USER wger
RUN git clone https://github.com/wger-project/wger.git /home/wger/src

WORKDIR /home/wger/src
RUN virtualenv --python python3 /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && invoke create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && invoke bootstrap_wger \
        --settings-path /home/wger/src/settings.py \
        --no-start-server


# Change permissions of some files and folders so the apache process
# can access them.
RUN chmod o+w -R ~/db/ \
    && . /home/wger/venv/bin/activate \
    && mkdir ~/static \
    && mkdir ~/media \
    && chmod o+w ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && python manage.py download-exercise-images \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py \
    && python manage.py collectstatic --noinput

USER root

ENTRYPOINT ["/usr/sbin/apache2ctl"]
CMD ["-D", "FOREGROUND"]

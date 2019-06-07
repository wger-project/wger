#
# A wger installation under apache with WSGI
#
# Please consult the documentation for usage
# docker build --tag wger/apache .
# docker run -ti --name wger.apache --publish 8000:80 wger/apache
#
#

FROM wger/base

LABEL maintainer="Roland Geider <roland@geider.net>"
EXPOSE 80

# Set locale to UTF8, otherwise problems with the encoding can occur, e.g.
# when using the invoke/wger commands and bower
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


# Install dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    apache2 \
    cron \
    libapache2-mod-wsgi-py3 \
  && rm -rf /var/lib/apt/lists/*

# Configure apache
ADD wger.conf /etc/apache2/sites-available/
RUN a2dissite 000-default.conf \
  && a2enmod headers \
  && a2ensite wger \
  && echo "ServerName localhost" >> /etc/apache2/conf-available/fqdn.conf \
  && a2enconf fqdn \
  && usermod -G wger www-data

# Configure cron
ADD crontab /etc/cron.d/wger
ADD venvwrapper /home/wger/venvwrapper

RUN chmod 0644 /etc/cron.d/wger \
  && chmod +x /home/wger/venvwrapper \
  && touch /var/log/cron.log

# Set up the application
RUN ln -s /home/wger/static/CACHE /var/www
USER wger
RUN git clone -b ${SOURCE_BRANCH:-master} https://github.com/wger-project/wger.git /home/wger/src \
  && git -C /home/wger/src rev-parse HEAD

WORKDIR /home/wger/src
RUN virtualenv --python python3 /home/wger/venv
RUN . /home/wger/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r requirements_forked.txt \
    && python setup.py develop \
    && wger create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
        --settings-path /home/wger/src/settings.py \
        --no-start-server


# Change permissions of some files and folders so the apache process
# can access them.
RUN chmod o+w -R ~/db/ \
    && . /home/wger/venv/bin/activate \
    && mkdir -p ~/static/CACHE ~/media \
    && ln -s /home/wger/static/CACHE /home/wger/src/CACHE \
    && chmod g+w /home/wger/static/CACHE \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && python manage.py download-exercise-images \
    && chmod -R g+w ~/media \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py \
    && python manage.py collectstatic --noinput

USER root

ENTRYPOINT ["/usr/sbin/apache2ctl"]
CMD ["-D", "FOREGROUND"]

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

# Set locale to UTF8, otherwise problems with the encoding can occur, e.g.
# when using the invoke/wger commands and bower
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


# Install dependencies
RUN apt-get install -y vim tmux sqlite3 python3-pip #python3-setuptools

# Set up the application
RUN git clone https://github.com/wger-project/wger.git /home/wger/src

WORKDIR /home/wger/src
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements_devel.txt \
    && pip3 install gunicorn redis django_redis psycopg2 \
    && python3 setup.py develop \
    && chown -R wger:wger .

USER wger
RUN wger create_settings \
        --settings-path /home/wger/src/settings.py \
        --database-path /home/wger/db/database.sqlite \
    && wger bootstrap \
        --settings-path /home/wger/src/settings.py \
        --no-start-server

# Install node modules for JS linting and download the exercise images
#
# Note: it seems there are problems with node and docker, so it's necessary
#       to delete the node_modules folder and install everything again
#       -> https://github.com/npm/npm/issues/9863
#       -> https://github.com/npm/npm/issues/13306
RUN cd wger \
    && rm -r node_modules \
    && npm install bower \
    && npm install \
    && cd .. \
    && mkdir ~/media \
    && sed -i "/^MEDIA_ROOT/c\MEDIA_ROOT='\/home\/wger\/media'" settings.py \
    && echo STATIC_ROOT=\'/home/wger/static\' >> settings.py \
    && echo CACHES = { >> settings.py \
    && echo "   'default': {" >> settings.py \
    && echo "       'BACKEND': 'django_redis.cache.RedisCache'," >> settings.py \
    && echo "       'TIMEOUT': '48000'," >> settings.py \
    && echo "       'LOCATION': 'redis://redis:6379/0'," >> settings.py \
    && echo "       'OPTIONS': {" >> settings.py \
    && echo "           'CLIENT_CLASS': 'django_redis.client.DefaultClient'" >> settings.py \
    && echo "           }" >> settings.py \
    && echo "       }" >> settings.py \
    && echo "    }" >> settings.py \
    && python3 manage.py collectstatic --noinput
#
#CACHES = {
#    "default": {
#        "BACKEND": "django_redis.cache.RedisCache",
#        "LOCATION": "redis://redis:6379/0",
#        "OPTIONS": {
#            "CLIENT_CLASS": "django_redis.client.DefaultClient",
#        }
#    }
#}


#    && python manage.py download-exercise-images


#ENTRYPOINT ["python3"]
CMD ["gunicorn", "wger.wsgi:application", "-w", "2", "-b", ":8000"]
#CMD ["manage.py", "runserver", "0.0.0.0:8000"]

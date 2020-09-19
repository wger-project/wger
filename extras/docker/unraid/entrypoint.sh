#!/bin/bash

# Copy a settings file if nothing's found (e.g. when mounting a fresh checkout)
if [ ! -f /home/wger/src/settings.py ]; then
   cp /tmp/settings.py /home/wger/src
fi

# If using docker compose, wait for postgres
if [[ "$DJANGO_DB_PORT" == "5432" ]]; then
    echo "Waiting for postgres..."

    while ! nc -z $DJANGO_DB_HOST $DJANGO_DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started :)"
fi

# Bootstrap the application
wger bootstrap

if [[ "$WGER_DOWNLOAD_IMGS" == "TRUE" ]];
then
    wger download-exercise-images
    chmod -R g+w ~wger/media
fi

# Run the server
if [ -z "$WGER_USE_GUNICORN" ]
then
    python3 manage.py runserver 0.0.0.0:8000
else
    gunicorn wger.wsgi:application --reload --bind 0.0.0.0:8000
fi



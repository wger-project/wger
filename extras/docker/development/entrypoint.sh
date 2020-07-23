#!/bin/bash

# Copy a settings file if not fould
if [ test ! -f /home/wger/src ]
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
wger bootstrap \
    --settings-path /home/wger/src/settings.py \
    --no-start-server

if [[ "$WGER_DOWNLOAD_IMGS" == "TRUE" ]];
then
    wger download-exercise-images
    chmod -R g+w ~wger/media
fi

# Run the development server
python3 manage.py runserver 0.0.0.0:8000

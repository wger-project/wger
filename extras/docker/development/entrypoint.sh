#!/bin/bash

cd /home/wger/src

if [[ "$DJANGO_DB_PORT" == "5432" ]]; then
    echo "Waiting for postgres..."

    while ! nc -z $DJANGO_DB_HOST $DJANGO_DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started :)"
fi

if [[ "$WGER_BOOTSTRAP" == "TRUE" ]];
then
    wger bootstrap \
        --settings-path /home/wger/src/settings.py \
        --no-start-server
fi

if [[ "$WGER_DOWNLOAD_IMGS" == "TRUE" ]];
then
    wger download-exercise-images
    chmod -R g+w ~wger/media
fi

#exec "$@"
python3 manage.py runserver 0.0.0.0:8000

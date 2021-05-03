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

# The python wger package needs to be installed in development mode.
# If the created folder does not exist (e.g. because this image was mounted
# after a first checkout), repeat the process.
if [ ! -d "/home/wger/src/wger.egg-info" ];
then
    python3 setup.py develop --user
fi

# Bootstrap the application
#   * Load the fixtures with exercises, ingredients, etc
#   * Create an admin user
#   * Download JS and CSS files
#   * Compile custom bootstrap theme
wger bootstrap

# Collect static files
if [[ "$DJANGO_DEBUG" == "False" ]];
then
    echo "Running in production mode, running collectstatic now"
    python3 manage.py collectstatic --no-input
fi

# Run the server
if [[ "$WGER_USE_GUNICORN" == "True" ]];
then
    echo "Using gunicorn..."
    gunicorn wger.wsgi:application --reload --bind 0.0.0.0:8000
else
    echo "Using django's development server..."
    python3 manage.py runserver 0.0.0.0:8000
fi

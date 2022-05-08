#!/bin/bash

# Copy a settings file if nothing's found (e.g. when mounting a fresh checkout)
if [ ! -f /home/wger/src/settings.py ]; then
   cp /tmp/settings.py /home/wger/src
fi


# The python wger package needs to be installed in development mode.
# If the created folder does not exist (e.g. because this image was mounted
# after a first checkout), repeat the process.
if [ ! -d "/home/wger/src/wger.egg-info" ];
then
    pip3 install -e .
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

# Perform database migrations
if [[ "$DJANGO_PERFORM_MIGRATIONS" == "True" ]];
then
    echo "Performing database migrations"
    python3 manage.py migrate
fi

# Sync exercises
if [[ "$SYNC_EXERCISES_ON_STARTUP" == "True" ]];
then
    echo "Synchronizing exercises"
    python3 manage.py sync-exercises
fi

# Download exercise images
if [[ "$DOWNLOAD_EXERCISE_IMAGES_ON_STARTUP" == "True" ]];
then
    echo "Downloading exercise images"
    python3 manage.py download-exercise-images
fi

# Set the site URL
python3 manage.py set-site-url

# Run the server
if [[ "$WGER_USE_GUNICORN" == "True" ]];
then
    echo "Using gunicorn..."
    gunicorn wger.wsgi:application --reload --bind 0.0.0.0:8000
else
    echo "Using django's development server..."
    python3 manage.py runserver 0.0.0.0:8000
fi

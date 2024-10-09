#!/bin/bash

# Copy a settings file if nothing's found (e.g. when mounting a fresh checkout)
# This is a bit ugly, but it's needed since we use this image for development
# and production.
if [ ! -f /home/wger/src/settings.py ]; then
   cp /tmp/settings.py /home/wger/src
fi


# The python wger package needs to be installed in development mode.
# If the created folder does not exist (e.g. because this image was mounted
# after a first checkout), repeat the process.
if [ ! -d "/home/wger/src/wger.egg-info" ];
then
    pip3 install --break-system-packages -e .
fi

# Bootstrap the application
#   * Load the fixtures with exercises, ingredients, etc
#   * Create an admin user
#   * (optionally) Download JS and CSS files
#   * (optionally) Compile custom bootstrap theme

if [ "$YARN_PROCESS_STATIC" == "True" ]; then
    yarn_static=""
else
    yarn_static="--no-process-static"
fi

wger bootstrap $yarn_static

# Collect static files
if [ "$DJANGO_CLEAR_STATIC_FIRST" == "False" ]; then
    clear=""
else
    clear="--clear"
fi

if [[ "$DJANGO_DEBUG" == "False" ]];
then
    echo "Running in production mode, running collectstatic now"
    python3 manage.py collectstatic --no-input $clear
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

# Download exercise videos
if [[ "$DOWNLOAD_EXERCISE_VIDEOS_ON_STARTUP" == "True" ]];
then
    echo "Downloading exercise videos"
    python3 manage.py download-exercise-videos
fi

# Load online fixtures
if [[ "$LOAD_ONLINE_FIXTURES_ON_STARTUP" == "True" ]];
then
    echo "Loading online fixtures"
    wger load-online-fixtures
fi

# Sync ingredients
if [[ "$SYNC_INGREDIENTS_ON_STARTUP" == "True" ]];
then
    echo "Syncing ingredients"
    python3 manage.py sync-ingredients
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

#!/bin/bash

# Bootstrap the application
#   * Load the fixtures with exercises, ingredients, etc
#   * Create an admin user
#   * (optionally) Download JS and CSS files
#   * (optionally) Compile custom bootstrap theme

# TODO: remove the warning after some time, e.g. after 2026-06-01
if [ "$YARN_PROCESS_STATIC" == "True" ];
then
    echo "The option YARN_PROCESS_STATIC has been removed as this step happens during "
    echo "the image's build process. If you really need this to run, manually call the "
    echo "bootstrap process with: 'docker compose exec web wger bootstrap'"
    exit 1
fi

wger bootstrap --no-process-static

# Collect static files
if [ "$DJANGO_CLEAR_STATIC_FIRST" == "False" ]; then
    clear_static=""
else
    clear_static="--clear"
fi

if [[ "$DJANGO_DEBUG" == "False" && "${DJANGO_COLLECTSTATIC_ON_STARTUP:-True}" == "True"  ]];
then
    echo "Running in production mode, running collectstatic now"
    python3 manage.py collectstatic --no-input $clear_static
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
    echo "The option SYNC_INGREDIENTS_ON_STARTUP is not supported anymore as it needs several hours to complete."
    echo "Please start the process manually with: docker compose exec web python3 manage.py sync-ingredients"
    exit 1
fi

# Set the site URL
python3 manage.py set-site-url

# Run the server
PORT="${WGER_PORT:-8000}"
if [[ "$WGER_USE_GUNICORN" == "True" ]];
then
    echo "Using gunicorn on port $PORT..."
    gunicorn wger.wsgi:application --preload --bind 0.0.0.0:$PORT
else
    echo "Using django's development server on port $PORT..."
    python3 manage.py runserver 0.0.0.0:$PORT
fi

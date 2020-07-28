#!/bin/sh

/home/wger/venvwrapper migrate

if [ "${DOWNLOAD_IMGS}" = "TRUE" ]; then
  /home/wger/venvwrapper download-exercise-images
  chmod -R g+w ~wger/media
fi

/home/wger/venvwrapper collectstatic --no-input
/home/wger/venvwrapper compress --force
chown www-data:www-data -R /home/wger/static

/usr/sbin/apache2ctl -D FOREGROUND

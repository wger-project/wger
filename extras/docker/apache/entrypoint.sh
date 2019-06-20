#!/bin/sh

/home/wger/venvwrapper migrate

if [ "${DOWNLOAD_IMGS}" = "TRUE" ]; then
  /home/wger/venvwrapper download-exercise-images
  chmod -R g+w ~wger/media
fi

if [ "${USE_S3}" = "TRUE" ]; then
  /home/wger/venvwrapper collectstatic --no-input
  /home/wger/venvwrapper compress --force
fi

/usr/sbin/apache2ctl -D FOREGROUND

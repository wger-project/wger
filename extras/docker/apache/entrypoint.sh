#!/bin/sh

if [ "${USE_S3}" = "TRUE" ]; then
  /home/wger/venvwrapper collectstatic --no-input
  /home/wger/venvwrapper compress
fi

/usr/sbin/apache2ctl -D FOREGROUND

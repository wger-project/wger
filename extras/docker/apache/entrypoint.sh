#!/bin/sh

if [ "${USE_S3}" = "TRUE" ]; then
  python manage.py collectstatic --no-input
fi

/usr/sbin/apache2ctl -D FOREGROUND

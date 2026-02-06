# Settings

This directory contains configuration files and settings for the project.

You can add your own configuration files here, e.g. for development. Set
the `DJANGO_SETTINGS_MODULE` environment variable to point to the new settings
file. E.g.:

```bash
export DJANGO_SETTINGS_MODULE=settings.local_dev
python manage.py runserver
```

If you want to add settings that are not tracked by git, you can create a
`local_dev_extra.py` file, this will be imported  by `local_dev.py` if it exists.

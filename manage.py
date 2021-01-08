#!/usr/bin/env python3

# Standard Library
import sys

# Django
from django.core.management import execute_from_command_line

# wger
from wger.tasks import (
    get_path,
    setup_django_environment
)


if __name__ == "__main__":

    # If user passed the settings flag ignore the default wger settings
    if not any('--settings' in s for s in sys.argv):
        setup_django_environment(get_path('settings.py'))

    # Alternative to above
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    execute_from_command_line(sys.argv)

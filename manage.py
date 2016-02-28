#!/usr/bin/env python
import sys

from django.core.management import execute_from_command_line

from wger.tasks import (
    setup_django_environment,
    get_user_config_path
)

if __name__ == "__main__":

    # Add the current directory to the system path. This is needed because
    # tasks.py removes it, read the comment the on why this clutch is needed.
    # Otherwise "local" setting files could not be imported
    sys.path.append('.')

    # If user passed the settings flag ignore the default wger settings
    if not any('--settings' in s for s in sys.argv):
        setup_django_environment(get_user_config_path('wger', 'settings.py'))

    # Alternative to above
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    execute_from_command_line(sys.argv)

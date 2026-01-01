#!/usr/bin/env python3

# Standard Library
import os
import sys

# Django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.main")
    execute_from_command_line(sys.argv)

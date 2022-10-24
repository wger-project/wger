"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

# Standard Library
import os

# Django
from django.conf import settings

# Third Party
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
app = Celery("wger")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover and load tasks.py from all registered Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def divide(x, y):
    # Standard Library
    import time
    time.sleep(5)
    return x / y

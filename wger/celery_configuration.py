#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
See https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

# Standard Library
import os

# Third Party
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
app = Celery("wger")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover and load tasks.py from all registered Django apps
app.autodiscover_tasks()

# @app.on_after_finalize.connect
#def setup_periodic_tasks(sender, **kwargs):
#    from wger.nutrition.tasks import test
#    sender.add_periodic_task(30.0, test.s('world'), expires=10)

# Calls test('hello') every 10 seconds.
#sender.add_periodic_task(
#    crontab(hour=7, minute=30, day_of_week=1),
#    test.s('Happy Mondays!'),
#)

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging
import random

# Django
from django.core.management import call_command

# Third Party
from celery.schedules import crontab

# wger
from wger.celery_configuration import app


logger = logging.getLogger(__name__)


@app.task
def flush_expired_jwt_tokens_task():
    """
    Delete OutstandingToken rows whose refresh token has already expired.

    With ROTATE_REFRESH_TOKENS enabled, every refresh creates a new
    OutstandingToken (and blacklists the previous one). Without periodic
    cleanup the table grows monotonically. simplejwt ships
    ``flushexpiredtokens`` for exactly this; cascading FK takes care of
    the matching BlacklistedToken rows.
    """
    call_command('flushexpiredtokens')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            hour=str(random.randint(0, 23)),
            minute=str(random.randint(0, 59)),
        ),
        flush_expired_jwt_tokens_task.s(),
        name='Flush expired JWT tokens',
    )

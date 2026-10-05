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
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.db.models import (
    Exists,
    OuterRef,
)

# Third Party
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.core.models import LongLivedSession
from wger.utils.mail import (
    get_delivery_connection,
    message_from_dict,
)


logger = logging.getLogger(__name__)


@app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
)
def send_email_task(payload: dict):
    """
    Deliver a single email, see wger.core.mail.CeleryEmailBackend
    """
    message = message_from_dict(payload)
    message.connection = get_delivery_connection()
    message.send()


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


@app.task
def flush_expired_long_lived_sessions_task():
    """
    Delete all expired DB-backed sessions and their index rows
    """
    SessionStore.clear_expired()

    # Index rows of sessions that are gone, the session table is the truth.
    LongLivedSession.objects.filter(
        ~Exists(Session.objects.filter(session_key=OuterRef('session_key')))
    ).delete()


@app.task
def flush_expired_oidc_tokens_task():
    """
    Delete expired access and refresh tokens of the OAuth2/OIDC provider.

    Rotation already drops the previous refresh token on every refresh, what
    stays behind are abandoned grants: tokens of applications that a user
    connected once and never used again.
    """
    call_command('oidc_cleartokens')


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
    sender.add_periodic_task(
        crontab(
            hour=str(random.randint(0, 23)),
            minute=str(random.randint(0, 59)),
        ),
        flush_expired_long_lived_sessions_task.s(),
        name='Flush expired long-lived sessions',
    )
    sender.add_periodic_task(
        crontab(
            hour=str(random.randint(0, 23)),
            minute=str(random.randint(0, 59)),
        ),
        flush_expired_oidc_tokens_task.s(),
        name='Flush expired OIDC tokens',
    )

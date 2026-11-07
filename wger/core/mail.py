#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
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
Email delivery through celery.

Sending an email means an SMTP round trip, which otherwise happens inside the
request that triggered it: registration, password reset, email change. This
backend only serializes the message and hands it to a worker, the real delivery
happens in EMAIL_DELIVERY_BACKEND.
"""

# Standard Library
import logging

# Django
from django.core.mail.backends.base import BaseEmailBackend

# Third Party
from celery.exceptions import OperationalError

# wger
from wger.core.tasks import send_email_task
from wger.utils.mail import (
    get_delivery_connection,
    message_to_dict,
)


logger = logging.getLogger(__name__)


class CeleryEmailBackend(BaseEmailBackend):
    """
    Email backend that queues the delivery instead of doing it in-band
    """

    def send_messages(self, email_messages) -> int:
        direct = []
        queued = 0

        for message in email_messages:
            payload = message_to_dict(message)
            if payload is None:
                direct.append(message)
                continue

            try:
                send_email_task.delay(payload)
            except OperationalError:
                # No broker. Delivering late is better than not at all, so
                # fall back to sending the message right here.
                logger.exception('Could not queue an email, sending it directly')
                direct.append(message)
            else:
                queued += 1

        if direct:
            queued += get_delivery_connection(self.fail_silently).send_messages(direct) or 0

        return queued

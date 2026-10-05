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
Turning email messages into something a celery task can carry.

See wger.core.mail for the backend that queues them and wger.core.tasks for
the task that delivers them.
"""

# Django
from django.conf import settings
from django.core.mail import (
    EmailMultiAlternatives,
    get_connection,
)


def get_delivery_connection(fail_silently: bool = False):
    """
    Connection to the backend that actually talks to the mail server
    """
    return get_connection(
        backend=settings.EMAIL_DELIVERY_BACKEND,
        fail_silently=fail_silently,
    )


def message_to_dict(message) -> dict | None:
    """
    Break a message down into the pieces a task can carry, or None if it
    contains something that would not survive the round trip.
    """
    if message.attachments:
        return None

    return {
        'subject': message.subject,
        'body': message.body,
        'from_email': message.from_email,
        'to': list(message.to),
        'cc': list(message.cc),
        'bcc': list(message.bcc),
        'reply_to': list(message.reply_to),
        'headers': dict(message.extra_headers),
        'content_subtype': message.content_subtype,
        'alternatives': [
            [content, mimetype] for content, mimetype in getattr(message, 'alternatives', [])
        ],
    }


def message_from_dict(data: dict) -> EmailMultiAlternatives:
    """
    Rebuild a message from the pieces of message_to_dict
    """
    message = EmailMultiAlternatives(
        subject=data['subject'],
        body=data['body'],
        from_email=data['from_email'],
        to=data['to'],
        cc=data['cc'],
        bcc=data['bcc'],
        reply_to=data['reply_to'],
        headers=data['headers'],
    )
    message.content_subtype = data['content_subtype']
    for content, mimetype in data['alternatives']:
        message.attach_alternative(content, mimetype)
    return message

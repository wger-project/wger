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
from unittest import mock

# Django
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.test import (
    SimpleTestCase,
    override_settings,
)
from django.urls import reverse

# Third Party
from celery.exceptions import OperationalError

# wger
from wger.core.tasks import send_email_task
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.mail import (
    message_from_dict,
    message_to_dict,
)


LOCMEM = 'django.core.mail.backends.locmem.EmailBackend'
CELERY = 'wger.core.mail.CeleryEmailBackend'
EXPLODING = 'wger.core.tests.test_mail.ExplodingBackend'


class ExplodingBackend(BaseEmailBackend):
    """
    Delivery backend that fails, unless it is told to keep quiet
    """

    def send_messages(self, email_messages):
        if not self.fail_silently:
            raise OSError('the mail server is not answering')
        return 0


def build_message():
    message = EmailMultiAlternatives(
        subject='Please confirm',
        body='plain text',
        from_email='wger@example.com',
        to=['user@example.com'],
        cc=['cc@example.com'],
        bcc=['bcc@example.com'],
        reply_to=['reply@example.com'],
        headers={'X-Wger': 'yes'},
    )
    message.attach_alternative('<p>html</p>', 'text/html')
    return message


@override_settings(EMAIL_BACKEND=CELERY, EMAIL_DELIVERY_BACKEND=LOCMEM)
class CeleryEmailBackendTestCase(SimpleTestCase):
    """
    Tests the email backend that hands the delivery to celery
    """

    def test_message_survives_the_round_trip(self):
        """
        Everything the message carries is restored from the task payload
        """
        original = build_message()

        restored = message_from_dict(message_to_dict(original))

        self.assertEqual(restored.subject, original.subject)
        self.assertEqual(restored.body, original.body)
        self.assertEqual(restored.from_email, original.from_email)
        self.assertEqual(restored.to, original.to)
        self.assertEqual(restored.cc, original.cc)
        self.assertEqual(restored.bcc, original.bcc)
        self.assertEqual(restored.reply_to, original.reply_to)
        self.assertEqual(restored.extra_headers, original.extra_headers)
        self.assertEqual(list(restored.alternatives), list(original.alternatives))

    def test_sending_only_queues(self):
        """
        The backend queues a task and does not talk to the mail server
        """
        with mock.patch('wger.core.tasks.send_email_task.delay') as delay:
            sent = build_message().send()

        self.assertEqual(sent, 1)
        self.assertEqual(delay.call_count, 1)
        self.assertEqual(mail.outbox, [])

    def test_task_delivers_the_message(self):
        """
        The task hands the rebuilt message to the delivery backend
        """
        payload = message_to_dict(build_message())

        send_email_task(payload)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Please confirm')
        self.assertEqual(mail.outbox[0].to, ['user@example.com'])
        self.assertEqual(mail.outbox[0].alternatives[0].content, '<p>html</p>')

    def test_message_with_attachment_is_sent_directly(self):
        """
        Attachments do not fit into the payload, those messages are delivered
        without the detour
        """
        message = build_message()
        message.attach('plan.csv', 'a,b,c', 'text/csv')

        with mock.patch('wger.core.tasks.send_email_task.delay') as delay:
            sent = message.send()

        self.assertEqual(sent, 1)
        self.assertEqual(delay.call_count, 0)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_DELIVERY_BACKEND=EXPLODING)
    def test_direct_delivery_keeps_fail_silently(self):
        """
        A caller that asked not to be bothered with delivery errors is not
        bothered with them on the direct path either
        """
        quiet = build_message()
        quiet.attach('plan.csv', 'a,b,c', 'text/csv')
        self.assertEqual(quiet.send(fail_silently=True), 0)

        # a fresh message, EmailMessage caches the connection it was sent with
        loud = build_message()
        loud.attach('plan.csv', 'a,b,c', 'text/csv')
        with self.assertRaises(OSError):
            loud.send(fail_silently=False)

    def test_unreachable_broker_falls_back_to_direct_delivery(self):
        """
        A message is delivered even when it cannot be queued
        """
        with mock.patch(
            'wger.core.tasks.send_email_task.delay',
            side_effect=OperationalError('no broker'),
        ):
            with self.assertLogs('wger.core.mail', level='ERROR'):
                sent = build_message().send()

        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)


@override_settings(EMAIL_BACKEND=CELERY, EMAIL_DELIVERY_BACKEND=LOCMEM)
class SignupEmailTestCase(WgerTestCase):
    """
    Tests that the emails of the registration flow are queued
    """

    def test_confirmation_email_is_queued(self):
        """
        Registering does not talk to the mail server during the request
        """
        data = {
            'username': 'mailtest',
            'password1': 'quai8fai7Zae',
            'password2': 'quai8fai7Zae',
            'email': 'mailtest@example.com',
        }

        with mock.patch('wger.core.tasks.send_email_task.delay') as delay:
            response = self.client.post(reverse('core:user:registration'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(delay.call_count, 1)
        self.assertEqual(mail.outbox, [])

        # and the queued payload is the confirmation email
        payload = delay.call_args[0][0]
        self.assertEqual(payload['to'], ['mailtest@example.com'])
        self.assertIn('Confirm', payload['subject'])

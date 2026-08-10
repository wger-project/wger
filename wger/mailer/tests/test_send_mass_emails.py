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

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.gym.models import Gym
from wger.mailer.models import (
    CronEntry,
    Log,
)


class SendMassEmailsTestCase(WgerTestCase):
    """
    Tests the command that works off the email queue
    """

    BATCH_SIZE = 100
    """The number of entries the command processes per run"""

    def setUp(self):
        super().setUp()
        self.log = Log(
            user=User.objects.get(username='admin'),
            gym=Gym.objects.get(pk=1),
            subject='Test subject',
            body='Test body',
        )
        self.log.save()

    def queue_entries(self, count: int):
        CronEntry.objects.bulk_create(
            [CronEntry(log=self.log, email=f'member{i}@example.com') for i in range(count)]
        )

    def test_empty_queue(self):
        call_command('send-mass-emails')

        self.assertEqual(len(mail.outbox), 0)

    def test_entries_are_sent_and_removed(self):
        self.queue_entries(3)

        call_command('send-mass-emails')

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(CronEntry.objects.count(), 0)

    def test_email_content_comes_from_the_log(self):
        self.queue_entries(1)

        call_command('send-mass-emails')

        message = mail.outbox[0]
        self.assertEqual(message.subject, 'Test subject')
        self.assertEqual(message.body, 'Test body')
        self.assertEqual(message.to, ['member0@example.com'])
        self.assertEqual(message.from_email, settings.WGER_SETTINGS['EMAIL_FROM'])

    def test_only_one_batch_per_run(self):
        """
        Larger queues are worked off over several runs
        """
        self.queue_entries(self.BATCH_SIZE + 20)

        call_command('send-mass-emails')

        self.assertEqual(len(mail.outbox), self.BATCH_SIZE)
        self.assertEqual(CronEntry.objects.count(), 20)

        call_command('send-mass-emails')

        self.assertEqual(len(mail.outbox), self.BATCH_SIZE + 20)
        self.assertEqual(CronEntry.objects.count(), 0)

    def test_the_log_entry_is_kept(self):
        """
        Only the queue entries are consumed, the log stays for the overview
        """
        self.queue_entries(2)

        call_command('send-mass-emails')

        self.assertTrue(Log.objects.filter(pk=self.log.pk).exists())

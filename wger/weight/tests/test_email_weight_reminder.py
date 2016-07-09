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

from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.weight.models import WeightEntry


class EmailWeightReminderTestCase(WorkoutManagerTestCase):
    def test_without_email(self):
        user = User.objects.get(pk=2)
        user.email = ''
        user.num_days_weight_reminder = 3
        user.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 0)

    def test_without_num_days_weight_reminder(self):
        user = User.objects.get(pk=2)
        user.email = 'test@test.com'
        user.save()

        user.userprofile.num_days_weight_reminder = 0
        user.userprofile.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 0)

    def test_with_num_days_weight_reminder(self):
        user = User.objects.get(pk=2)
        user.email = 'test@test.com'
        user.save()

        user.userprofile.num_days_weight_reminder = 3
        user.userprofile.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email(self):
        user = User.objects.get(pk=2)
        user.email = 'test@test.com'
        user.save()

        weightEntry = WeightEntry.objects.filter(user=user).get(pk=3)
        weightEntry.date = datetime.now().date() - timedelta(days=2)
        weightEntry.save()

        user.userprofile.num_days_weight_reminder = 1
        user.userprofile.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_zero_days_diff(self):
        user = User.objects.get(pk=2)
        user.email = 'test@test.com'
        user.save()

        weightEntry = WeightEntry.objects.filter(user=user).get(pk=3)
        weightEntry.date = datetime.now().date() - timedelta(days=1)
        weightEntry.save()

        user.userprofile.num_days_weight_reminder = 1
        user.userprofile.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 1)

    def test_not_send_email(self):
        user = User.objects.get(pk=2)
        user.email = 'test@test.com.br'
        user.save()

        weightEntry = WeightEntry.objects.filter(user=user).latest()
        weightEntry.date = datetime.now().date()
        weightEntry.save()

        user.userprofile.num_days_weight_reminder = 3
        user.userprofile.save()

        call_command("email-weight-reminder")
        self.assertEqual(len(mail.outbox), 0)

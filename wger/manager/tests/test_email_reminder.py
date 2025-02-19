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
import datetime

# Django
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command

# wger
from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Routine


class EmailReminderTestCase(WgerTestCase):
    """
    Tests the email reminder command.

    User 2 has setting in profile active
    """

    def setUp(self):
        super().setUp()

        routine = Routine.objects.get(pk=2)
        routine.start = datetime.date.today() - datetime.timedelta(weeks=10)
        routine.end = datetime.date.today() - datetime.timedelta(days=3)
        routine.save()

    def test_reminder_no_workouts(self):
        """
        Test with no schedules or workouts
        """
        Routine.objects.all().delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_one_workout(self):
        """
        Test user with no schedules but one workout
        """
        Routine.objects.exclude(user_id=2).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_skip_if_no_email(self):
        """
        Tests that no emails are sent if the user has provided no email
        """

        user = User.objects.get(pk=2)
        user.email = ''
        user.save()

        Routine.objects.exclude(user_id=2).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_last_notification(self):
        """
        Test that no emails are sent if the last notification field is more
        recent than one week.
        """

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = datetime.date.today() - datetime.timedelta(days=3)
        profile.save()

        Routine.objects.exclude(user_id=2).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_last_notification_2(self):
        """
        Test that no emails are sent if the last notification field is more
        than one week away.
        """

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = datetime.date.today() - datetime.timedelta(days=10)
        profile.save()

        Routine.objects.exclude(user_id=2).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_last_notification_3(self):
        """
        Test that no emails are sent if the last notification field is null

        User 2, workout created 2012-11-20
        """

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = None
        profile.save()

        Routine.objects.exclude(user_id=2).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_setting_off(self):
        """
        Test user with one routine but setting in profile off
        """

        user = User.objects.get(pk=2)
        user.userprofile.workout_reminder_active = False
        user.userprofile.save()
        Routine.objects.exclude(user=user).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

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

import datetime

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command

from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.manager.models import Schedule
from wger.manager.models import Workout


class EmailReminderTestCase(WorkoutManagerTestCase):
    '''
    Tests the email reminder command.

    User 2 has setting in profile active
    '''

    def test_reminder_no_workouts(self):
        '''
        Test with no schedules or workouts
        '''
        Schedule.objects.all().delete()
        Workout.objects.all().delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_one_workout(self):
        '''
        Test user with no schedules but one workout

        User 2, workout created 2012-11-20
        '''

        Schedule.objects.all().delete()
        Workout.objects.exclude(user=User.objects.get(pk=2)).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_skip_if_no_email(self):
        '''
        Tests that no emails are sent if the user has provided no email

        User 2, workout created 2012-11-20
        '''

        user = User.objects.get(pk=2)
        user.email = ''
        user.save()

        Schedule.objects.all().delete()
        Workout.objects.exclude(user=User.objects.get(pk=2)).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_last_notification(self):
        '''
        Test that no emails are sent if the last notification field is more
        recent than one week.

        User 2, workout created 2012-11-20
        '''

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = datetime.date.today() - datetime.timedelta(days=3)
        profile.save()

        Schedule.objects.all().delete()
        Workout.objects.exclude(user=User.objects.get(pk=2)).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_last_notification_2(self):
        '''
        Test that no emails are sent if the last notification field is more
        than one week away.

        User 2, workout created 2012-11-20
        '''

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = datetime.date.today() - datetime.timedelta(days=10)
        profile.save()

        Schedule.objects.all().delete()
        Workout.objects.exclude(user=User.objects.get(pk=2)).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_last_notification_3(self):
        '''
        Test that no emails are sent if the last notification field is null

        User 2, workout created 2012-11-20
        '''

        profile = UserProfile.objects.get(user=2)
        profile.last_workout_notification = None
        profile.save()

        Schedule.objects.all().delete()
        Workout.objects.exclude(user=User.objects.get(pk=2)).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_setting_off(self):
        '''
        Test user with no schedules, one workout but setting in profile off
        '''

        user = User.objects.get(pk=2)
        user.userprofile.workout_reminder_active = False
        user.userprofile.save()
        Schedule.objects.all().delete()
        Workout.objects.exclude(user=user).delete()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_empty_schedule(self):
        '''
        Test user with emtpy schedules and no workouts
        '''

        user = User.objects.get(pk=2)
        user.userprofile.workout_reminder_active = False
        user.userprofile.save()
        Schedule.objects.all().delete()
        Workout.objects.all().delete()

        schedule = Schedule()
        schedule.user = user
        schedule.is_active = True
        schedule.is_loop = False
        schedule.name = 'test schedule'
        schedule.start_date = datetime.date(2013, 1, 10)

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_schedule(self):
        '''
        Test user with a schedule and a workout
        '''

        user = User.objects.get(pk=2)
        Workout.objects.exclude(user=user).delete()
        Schedule.objects.exclude(user=user).delete()
        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_schedule_recent(self):
        '''
        Test user with a schedule that has not finished
        '''

        user = User.objects.get(pk=1)
        user.userprofile.workout_reminder_active = True
        user.userprofile.save()
        Workout.objects.exclude(user=user).delete()
        Schedule.objects.exclude(user=user).delete()

        schedule = Schedule.objects.get(pk=2)
        schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=4)
        schedule.is_active = True
        schedule.is_loop = False
        schedule.save()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_schedule_recent_2(self):
        '''
        Test user with a schedule that is about to finish
        '''

        user = User.objects.get(pk=1)
        user.userprofile.workout_reminder_active = True
        user.userprofile.save()
        Workout.objects.exclude(user=user).delete()
        Schedule.objects.exclude(user=user).delete()

        # Schedule: 3, 5 and 2 weeks
        schedule = Schedule.objects.get(pk=2)
        schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=9)
        schedule.is_active = True
        schedule.is_loop = False
        schedule.save()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_reminder_schedule_recent_3(self):
        '''
        Test user with a schedule that is about to finish
        '''

        user = User.objects.get(pk=1)
        user.userprofile.workout_reminder_active = True
        user.userprofile.workout_reminder = 5
        user.userprofile.save()
        Workout.objects.exclude(user=user).delete()
        Schedule.objects.exclude(user=user).delete()

        # Schedule: 3, 5 and 2 weeks
        schedule = Schedule.objects.get(pk=2)
        schedule.start_date = datetime.date.today() - datetime.timedelta(weeks=9)
        schedule.is_active = True
        schedule.is_loop = False
        schedule.save()

        call_command('email-reminders')
        self.assertEqual(len(mail.outbox), 0)

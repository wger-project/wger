# -*- coding: utf-8 *-*

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

from django.template import loader
from django.core.management.base import BaseCommand
from django.core import mail
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.conf import settings

from django.contrib.sites.models import Site
from wger.core.models import UserProfile
from wger.manager.models import Schedule


class Command(BaseCommand):
    '''
    Helper admin command to send out email reminders
    '''

    help = 'Send out automatic email reminders for workouts'

    def handle(self, **options):
        '''
        Find if the currently active workout is overdue
        '''
        profile_list = UserProfile.objects.filter(workout_reminder_active=True)
        counter = 0
        for profile in profile_list:

            # Only continue if the user has provided an email address.
            # Checking it here so we check for NULL values and emtpy strings
            if not profile.user.email:
                continue

            # Check if we already notified the user and update the profile otherwise
            if profile.last_workout_notification and \
               (datetime.date.today()
                    - profile.last_workout_notification
                    < datetime.timedelta(weeks=1)):
                continue

            (current_workout, schedule) = Schedule.objects.get_current_workout(profile.user)

            # No schedules, use the default workout length in user profile
            if not schedule and current_workout:
                delta = (current_workout.creation_date
                         + datetime.timedelta(weeks=profile.workout_duration)
                         - datetime.date.today())

                if datetime.timedelta(days=profile.workout_reminder) > delta:
                    if int(options['verbosity']) >= 3:
                        self.stdout.write("* Workout '{0}' overdue".format(current_workout))
                    counter += 1

                    self.send_email(profile.user,
                                    current_workout,
                                    delta)

            # non-loop schedule, take the step's duration
            elif schedule and not schedule.is_loop:

                schedule_step = schedule.get_current_scheduled_workout()

                # Only notify if the step is the last one in the schedule
                if schedule_step == schedule.schedulestep_set.last():

                    delta = schedule.get_end_date() - datetime.date.today()
                    if datetime.timedelta(days=profile.workout_reminder) > delta:
                        if int(options['verbosity']) >= 3:
                            self.stdout.write("* Workout '{0}' overdue - schedule".
                                              format(schedule_step.workout))

                        counter += 1
                        self.send_email(profile.user,
                                        current_workout,
                                        delta)

        if counter and int(options['verbosity']) >= 2:
            self.stdout.write("Sent {0} email reminders".format(counter))

    @staticmethod
    def send_email(user, workout, delta):
        '''
        Notify a user that a workout is about to expire

        :type user User
        :type workout Workout
        :type delta datetime.timedelta
        '''

        # Update the last notification date field
        user.userprofile.last_workout_notification = datetime.date.today()
        user.userprofile.save()

        # Compose and send the email
        translation.activate(user.userprofile.notification_language.short_name)
        context = {'site': Site.objects.get_current(),
                   'workout': workout,
                   'expired': True if delta.days < 0 else False,
                   'days': abs(delta.days)}

        subject = _('Workout will expire soon')
        message = loader.render_to_string('workout/email_reminder.tpl', context)
        mail.send_mail(subject,
                       message,
                       settings.WGER_SETTINGS['EMAIL_FROM'],
                       [user.email],
                       fail_silently=True)

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

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core import mail
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import translation
from django.core.urlresolvers import reverse

from django.contrib.sites.models import Site
from wger.manager.models import UserProfile
from wger.manager.models import Schedule
from wger.manager.models import Workout
from wger.utils.constants import EMAIL_FROM


class Command(BaseCommand):
    '''
    Helper admin command to send out email remainders
    '''

    help = 'Send out automatic email remainders for workouts'

    def handle(self, *args, **options):
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
            else:
                profile.last_workout_notification = datetime.date.today()
                profile.save()

            (current_workout, schedule) = Schedule.objects.get_current_workout(profile.user)

            # No schedules, use the default workout length in user profile
            if not schedule and current_workout:
                delta = (current_workout.creation_date
                         + datetime.timedelta(weeks=profile.workout_duration)
                         - datetime.date.today())

                if datetime.timedelta(days=profile.workout_reminder) > delta:
                    if int(options['verbosity']) >= 3:
                        print "* Workout '{0}' overdue".format(current_workout)
                    counter += 1
                    self.send_email(profile.user,
                                    current_workout,
                                    profile.workout_duration)

            # non-loop schedule, take the step's duration
            elif schedule and not schedule.is_loop:

                schedule_step = schedule.get_current_scheduled_workout()

                # Only notify if the step is the last one in the schedule
                # TODO: this could be simplified using last(), introduced in django 1.6
                step_list = [step for step in schedule.schedulestep_set.all()]
                if schedule_step == step_list[-1]:

                    delta = schedule.get_end_date() - datetime.date.today()
                    if datetime.timedelta(days=profile.workout_reminder) > delta:
                        if int(options['verbosity']) >= 3:
                            print "* Workout '{0}' overdue - schedule".format(schedule_step.workout)

                        counter += 1
                        self.send_email(profile.user,
                                        current_workout,
                                        profile.workout_duration)

        if counter and int(options['verbosity']) >= 2:
            self.stdout.write("Sent {0} email reminders".format(counter))

    @staticmethod
    def send_email(user, workout, days):
        '''
        Notify a user that a workout is about to expire

        :type user User
        :type workout Workout
        :type days int
        '''

        translation.activate(user.userprofile.notification_language.short_name)
        site = Site.objects.get(pk=settings.SITE_ID)
        workout_link = 'http://{0}{1}'.format(site.domain, workout.get_absolute_url())
        add_workout_link = 'http://{0}{1}'.format(site.domain, reverse('workout-add'))
        settings_link = 'http://{0}{1}'.format(site.domain, reverse('preferences'))

        subject = _('Workout will expire soon')
        message = _("Your current workout '{workout}' is about to expire in {days} days.\n\n"
                    ""
                    "You will regularly receive such reminders till you add a new workout.\n"
                    "Alternatively you can add workouts to a loop schedule, such schedules\n"
                    "never produce reminders. If you don't want to ever receive email\n"
                    "reminders, deactivate the option in your settings.\n\n"
                    ""
                    "* {add_workout_link}\n"
                    "* {workout_link}\n"
                    "* {settings_link}"
                    ).format(workout=workout,
                             days=days,
                             workout_link=workout_link,
                             add_workout_link=add_workout_link,
                             settings_link=settings_link)
        mail.send_mail(subject,
                       message,
                       EMAIL_FROM,
                       [user.email],
                       fail_silently=True)

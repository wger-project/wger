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
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.management.base import BaseCommand
from django.template import loader
from django.utils import translation
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import UserProfile
from wger.manager.models import Routine


class Command(BaseCommand):
    """
    Helper admin command to send out email reminders
    """

    help = 'Send out automatic email reminders for workouts'

    def handle(self, **options):
        """
        Find if the currently active workout is overdue
        """
        profile_list = UserProfile.objects.filter(workout_reminder_active=True)
        counter = 0
        today = datetime.date.today()

        for profile in profile_list:
            if not profile.user.email:
                continue

            routine = Routine.objects.filter(user=profile.user).last()
            if not routine:
                continue

            delta = routine.end - datetime.date.today()

            if delta.days < 0:
                # Skip if notified this week:
                if profile.last_workout_notification and (
                    today - profile.last_workout_notification < datetime.timedelta(weeks=1)
                ):
                    continue

                if int(options['verbosity']) >= 3:
                    self.stdout.write(f"* Routine '{routine}' overdue")

                self.send_email(profile.user, routine, delta)
                profile.last_workout_notification = today
                profile.save()

        if counter and int(options['verbosity']) >= 2:
            self.stdout.write(f'Sent {counter} email reminders')

    @staticmethod
    def send_email(user, routine: Routine, delta: datetime.timedelta):
        """
        Notify a user that a workout is about to expire
        """

        # Compose and send the email
        translation.activate(user.userprofile.notification_language.short_name)
        context = {
            'site': Site.objects.get_current(),
            'routine': routine,
            'expired': delta.days < 0,
            'days': abs(delta.days),
        }

        subject = _('Routine will expire soon')
        message = loader.render_to_string('routines/email_reminder.tpl', context)
        mail.send_mail(
            subject,
            message,
            settings.WGER_SETTINGS['EMAIL_FROM'],
            [user.email],
            fail_silently=True,
        )

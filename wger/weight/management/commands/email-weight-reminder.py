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
from wger.weight.models import WeightEntry


class Command(BaseCommand):
    '''
    Helper admin command to send out email reminders
    '''

    help = 'Send out automatic emails to remind the user to enter the weight'

    def handle(self, **options):

        profile_list = UserProfile.objects.filter(num_days_weight_reminder__gt=0)

        for profile in profile_list:

            # Only continue if the user has provided an email address.
            # Checking it here so we check for NULL values and emtpy strings
            if not profile.user.email:
                continue

            today = datetime.datetime.now().date()

            try:
                last_entry = WeightEntry.objects.filter(user=profile.user).latest().date
                datediff = (today - last_entry).days

                if datediff >= profile.num_days_weight_reminder:
                    self.send_email(profile.user, last_entry, datediff)
            except WeightEntry.DoesNotExist:
                pass

    @staticmethod
    def send_email(user, last_entry, datediff):
        '''
        Notify a user to input the weight entry

        :type user User
        :type last_entry Date
        '''

        # Compose and send the email
        translation.activate(user.userprofile.notification_language.short_name)

        context = {'site': Site.objects.get_current(),
                   'date': last_entry,
                   'days': datediff,
                   'user': user}

        subject = _('You have to enter your weight')
        message = loader.render_to_string('workout/email_weight_reminder.tpl', context)
        mail.send_mail(subject,
                       message,
                       settings.WGER_SETTINGS['EMAIL_FROM'],
                       [user.email],
                       fail_silently=True)

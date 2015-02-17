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

from django.contrib.sites.models import Site
from wger.core.models import UserProfile
from wger.weight.models import WeightEntry
from wger.utils.constants import EMAIL_FROM


class Command(BaseCommand):
    '''
    Helper admin command to send out email remainders
    '''

    help = 'Send out automatic emails to reminder the user to input the weight'

    def handle(self, *args, **options):

        profile_list = UserProfile.objects.filter(num_days_weight_reminder__gt=0)

        for profile in profile_list:

            # Onl continue if the user has provided an email address.
            # Checking it here so we check for NULL values and emtpy strings
            #print("Checking User RWeight Reminder")
            if not profile.user.email:
                continue

            today = datetime.datetime.now().date()
            #print(today)

            try:
                last_entry = WeightEntry.objects.filter(user=profile.user).latest().creation_date
                datediff = (today - last_entry).days

                if datediff >= profile.num_days_weight_reminder:
                    self.send_email(profile.user, last_entry)
            except WeightEntry.DoesNotExist:
                print("At least one weight entry is required")


    @staticmethod
    def send_email(user, last_entry):
        '''
        Notify a user to input the weight entry

        :type user User
        :type last_entry Date
        '''

        # Compose and send the email
        translation.activate(user.userprofile.notification_language.short_name)

        context = {}
        context['site'] = Site.objects.get_current()
        context['day'] = last_entry

        subject = _('You have to entry your weight')
        message = loader.render_to_string('workout/email_weight_reminder.html', context)
        mail.send_mail(subject,
                       message,
                       EMAIL_FROM,
                       [user.email],
                       fail_silently=True)

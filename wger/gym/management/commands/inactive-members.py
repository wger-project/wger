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

from django.core import mail
from django.utils import translation
from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings

from wger.gym.helpers import is_any_gym_admin
from wger.gym.models import Gym


class Command(BaseCommand):
    '''
    Sends overviews of inactive users to gym trainers
    '''
    help = 'Send out emails to trainers with users that have not shown recent activity'

    def handle(self, **options):
        '''
        Process gyms and send emails
        '''

        today = datetime.date.today()

        for gym in Gym.objects.all():
            if int(options['verbosity']) >= 2:
                self.stdout.write("* Processing gym '{}' ".format(gym))

            user_list = []
            trainer_list = []
            user_list_no_activity = []
            weeks = gym.config.weeks_inactive

            if not weeks:
                if int(options['verbosity']) >= 2:
                    self.stdout.write("  Reminders deactivatd, skipping")
                continue

            for profile in gym.userprofile_set.all():
                user = profile.user

                # check if the account was deactivated (user can't login)
                if not user.is_active:
                    continue

                # add to trainer list that will be notified
                if user.has_perm('gym.gym_trainer'):
                    trainer_list.append(user)

                # Check appropriate permissions
                if is_any_gym_admin(user):
                    continue

                # Check user preferences
                if not user.gymuserconfig.include_inactive:
                    continue

                last_activity = user.usercache.last_activity
                if not last_activity:
                    user_list_no_activity.append({'user': user, 'last_activity': last_activity})
                elif today - last_activity > datetime.timedelta(weeks=weeks):
                    user_list.append({'user': user, 'last_activity': last_activity})

            if user_list or user_list_no_activity:
                for trainer in trainer_list:

                    # Profile might not have email
                    if not trainer.email:
                        continue

                    # Check trainer preferences
                    if not trainer.gymadminconfig.overview_inactive:
                        continue

                    translation.activate(trainer.userprofile.notification_language.short_name)
                    subject = _('Reminder of inactive members')
                    context = {
                        'weeks': weeks,
                        'user_list': user_list,
                        'user_list_no_activity': user_list_no_activity
                    }
                    message = render_to_string('gym/email_inactive_members.html', context)
                    mail.send_mail(subject,
                                   message,
                                   settings.WGER_SETTINGS['EMAIL_FROM'],
                                   [trainer.email],
                                   fail_silently=True)

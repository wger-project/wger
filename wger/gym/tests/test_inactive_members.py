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

from django.core import mail
from django.core.management import call_command

from wger.core.tests.base_testcase import WorkoutManagerTestCase


class EmailInactiveUserTestCase(WorkoutManagerTestCase):
    '''
    Test email reminders for inactive users
    '''

    def test_reminder(self, fail=False):
        '''
        Test email reminders for inactive users
        '''

        call_command('inactive-members')
        self.assertEqual(len(mail.outbox), 6)

        recipment_list = [message.to[0] for message in mail.outbox]
        trainer_list = ['trainer4@example.com',
                        'trainer5@example.com',
                        'trainer1@example.com',
                        'trainer2@example.com',
                        'trainer3@example.com']
        recipment_list.sort()
        trainer_list.sort()

        self.assertEqual(recipment_list.sort(), trainer_list.sort())

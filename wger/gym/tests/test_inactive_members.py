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

# Django
from django.core import mail
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase


class EmailInactiveUserTestCase(WgerTestCase):
    """
    Test email reminders for inactive users
    """

    def test_reminder(self):
        """
        Test email reminders for inactive users
        """

        call_command('inactive-members')

        # Everybody in the gym with the gym_trainer permission and the
        # overview_inactive preference gets the overview, including the admin
        recipient_list = [message.to[0] for message in mail.outbox]
        self.assertCountEqual(
            recipient_list,
            [
                'admin@example.com',
                'trainer1@example.com',
                'trainer2@example.com',
                'trainer3@example.com',
                'trainer4@example.com',
                'trainer5@example.com',
            ],
        )

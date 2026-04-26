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
import csv
import datetime
import io

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.gym.models import Gym


class GymMembersCsvExportTestCase(WgerTestCase):
    """
    Test case for the CSV export of gym members
    """

    def export_csv(self, fail=True):
        """
        Helper function to test the CSV export
        """
        response = self.client.get(reverse('gym:export:users', kwargs={'gym_pk': 1}))
        gym = Gym.objects.get(pk=1)

        if fail:
            self.assertIn(response.status_code, (403, 302))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')

            today = datetime.date.today()
            filename = 'User-data-gym-{gym}-{t.year}-{t.month:02d}-{t.day:02d}.csv'.format(
                t=today, gym=gym.id
            )
            self.assertEqual(response['Content-Disposition'], f'attachment; filename={filename}')
            self.assertGreaterEqual(len(response.content), 1000)
            self.assertLessEqual(len(response.content), 1300)

    def test_export_csv_authorized(self):
        """
        Test the CSV export by authorized users
        """

        for username in ('manager1', 'manager2', 'general_manager1'):
            self.user_login(username)
            self.export_csv(fail=False)

    def test_export_csv_unauthorized(self):
        """
        Test the CSV export by unauthorized users
        """

        for username in (
            'manager3',
            'manager4',
            'test',
            'member1',
            'member2',
            'member3',
            'member4',
            'member5',
        ):
            self.user_login(username)
            self.export_csv(fail=True)

    def test_export_csv_logged_out(self):
        """
        Test the CSV export by a logged out user
        """
        self.user_logout()
        self.export_csv(fail=True)

    def test_export_neutralises_csv_formula_payload(self):
        member = User.objects.get(username='member1')
        member.first_name = '=HYPERLINK("http://attacker.example", "click")'
        member.last_name = '+SUM(1+2)'
        member.save()
        member.userprofile.phone = '@evil'
        member.userprofile.city = '-bad'
        member.userprofile.save()

        self.user_login('manager1')
        response = self.client.get(reverse('gym:export:users', kwargs={'gym_pk': 1}))
        self.assertEqual(response.status_code, 200)

        rows = list(csv.reader(io.StringIO(response.content.decode()), delimiter='\t'))
        member_row = next(row for row in rows if row and row[2] == 'member1')

        for cell in member_row:
            if cell:
                self.assertNotIn(
                    cell[0],
                    ('=', '+', '-', '@'),
                    msg=f'unsanitised formula cell in export: {cell!r}',
                )

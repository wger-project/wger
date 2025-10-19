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
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


# TODO: parse the generated calendar files with the icalendar library


class WorkoutICalExportTestCase(WgerTestCase):
    """
    Tests exporting the ical file for a workout
    """

    def export_ical(self, fail=False):
        """
        Helper function
        """

        response = self.client.get(reverse('manager:routine:ical', kwargs={'pk': 3}))

        if fail:
            self.assertIn(response.status_code, (403, 404))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/calendar')

            # Approximate size
            self.assertGreater(len(response.content), 50)
            self.assertLess(len(response.content), 620)

    def test_export_ical_anonymous(self):
        """
        Tests exporting a workout as an ical file as an anonymous user
        """

        self.export_ical(fail=True)

    def test_export_ical_owner(self):
        """
        Tests exporting a workout as an ical file as the owner user
        """

        self.user_login('test')
        self.export_ical(fail=False)

    def test_export_ical_other(self):
        """
        Tests exporting a workout as an ical file as a logged user not owning the data
        """

        self.user_login('admin')
        self.export_ical(fail=True)

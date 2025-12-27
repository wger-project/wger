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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import datetime

# Django
from django.urls import reverse

# wger
from wger.core.models import RepetitionUnit
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Routine


class AddTimedExerciseViewTest(WgerTestCase):
    """
    Tests for the add_timed_exercise view
    """

    def test_requires_login(self):
        """Test that anonymous users are redirected to login"""
        response = self.client.get(reverse('manager:add-timed-exercise'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_get_form(self):
        """Test that logged in users can access the form"""
        self.user_login('admin')
        response = self.client.get(reverse('manager:add-timed-exercise'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_timed_exercise.html')

    def test_form_shows_only_time_units(self):
        """Test that the unit dropdown only shows TIME units"""
        self.user_login('admin')
        response = self.client.get(reverse('manager:add-timed-exercise'))
        form = response.context['form']
        unit_queryset = form.fields['unit'].queryset
        for unit in unit_queryset:
            self.assertEqual(unit.unit_type, RepetitionUnit.UNIT_TYPE_TIME)


class GetDaysForRoutineViewTest(WgerTestCase):
    """
    Tests for the get_days_for_routine AJAX endpoint
    """

    def test_requires_login(self):
        """Test that anonymous users are redirected"""
        response = self.client.get(reverse('manager:api-days', kwargs={'routine_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_returns_days_for_user_routine(self):
        """Test that endpoint returns days for user's routine"""
        self.user_login('admin')
        # Create a routine for admin user
        routine = Routine.objects.create(
            user_id=1,
            name='Test Routine',
            start=datetime.date.today(),
            end=datetime.date.today() + datetime.timedelta(days=30),
        )
        response = self.client.get(reverse('manager:api-days', kwargs={'routine_id': routine.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

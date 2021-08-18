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
from wger.manager.models import Workout


class WorkoutTemplateManagerTestCase(WgerTestCase):
    """
    Test accessing the workout template DB manager
    """

    def test_managers(self):
        """
        Test that the DB managers correctly filter the workouts
        """
        self.assertEqual(Workout.objects.all().count(), 3)
        self.assertEqual(Workout.templates.all().count(), 0)
        self.assertEqual(Workout.both.all().count(), 3)

        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.save()
        self.assertEqual(Workout.objects.all().count(), 2)
        self.assertEqual(Workout.templates.all().count(), 1)
        self.assertEqual(Workout.both.all().count(), 3)

        workout.is_public = True
        workout.save()
        self.assertEqual(Workout.objects.all().count(), 2)
        self.assertEqual(Workout.templates.all().count(), 1)
        self.assertEqual(Workout.both.all().count(), 3)


class WorkoutTemplateOverviewTestCase(WgerTestCase):
    """
    Test accessing the workout template overview page
    """

    def test_access_overviews(self):
        """
        Test accessing the different workout and template overviews
        """
        self.user_login('test')
        response = self.client.get(reverse('manager:workout:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 1)

        response = self.client.get(reverse('manager:template:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 0)

        response = self.client.get(reverse('manager:template:public'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 0)

    def test_access_overviews_no_public_templates(self):
        """
        Test accessing the different workout and template overviews - no public workouts
        """

        # Workout #1 belongs to another user
        workout = Workout.objects.get(pk=1)
        workout.is_template = True
        workout.save()

        self.user_login('test')
        response = self.client.get(reverse('manager:workout:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 1)

        response = self.client.get(reverse('manager:template:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 0)

        response = self.client.get(reverse('manager:template:public'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 0)

    def test_access_overviews_public_templates(self):
        """
        Test accessing the different workout and template overviews - no public workouts
        """
        workout = Workout.objects.get(pk=1)
        workout.is_template = True
        workout.is_public = True
        workout.save()

        self.user_login('test')
        response = self.client.get(reverse('manager:workout:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 1)

        response = self.client.get(reverse('manager:template:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 0)

        response = self.client.get(reverse('manager:template:public'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['workouts']), 1)


class WorkoutTemplateDetailPageTestCase(WgerTestCase):
    """
    Test accessing the workout template detail page
    """

    def test_access_detail_for_workout(self):
        """
        Test accessing the template view for a regular workout
        """
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 302)

        self.user_login('test')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 404)

        self.user_login('admin')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 404)

    def test_access_detail_for_template(self):
        """
        Test accessing the template view for a template
        """
        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.save()

        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 302)

        self.user_login('test')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 200)
        self.user_logout()

        self.user_login('admin')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 403)

    def test_access_detail_for_public_template(self):
        """
        Test accessing the template view for a template
        """
        workout = Workout.objects.get(pk=3)
        workout.is_template = True
        workout.is_public = True
        workout.save()

        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 302)

        self.user_login('test')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 200)
        self.user_logout()

        self.user_login('admin')
        response = self.client.get(reverse('manager:template:view', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 200)


class SwitchViewsTestCase(WgerTestCase):
    """
    Test the views that convert a workout to a template and viceversa
    """

    def test_make_template(self):
        """
        Test accessing the template view for a regular workout
        """
        response = self.client.get(reverse('manager:workout:make-template', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 403)

        self.user_login('test')
        response = self.client.get(reverse('manager:workout:make-template', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 200)

        self.user_login('admin')
        response = self.client.get(reverse('manager:workout:make-template', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 403)

    def test_make_workout(self):
        """
        Test marking a template a workout again
        """
        response = self.client.get(reverse('manager:template:make-workout', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 403)

        self.user_login('test')
        response = self.client.get(reverse('manager:template:make-workout', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 302)

        self.user_login('admin')
        response = self.client.get(reverse('manager:template:make-workout', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 403)

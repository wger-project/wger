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
import json

# Django
from django.core.cache import cache
from django.template import (
    Context,
    Template,
)
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import ExerciseCrudApiTestCase
from wger.core.tests.base_testcase import (
    WgerDeleteTestCase,
    WgerTestCase,
)
from wger.exercises.models import (
    Exercise,
    Muscle,
)
from wger.utils.cache import cache_mapper
from wger.utils.constants import CC_BY_SA_4_ID


class ExerciseRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(str(Exercise.objects.get(pk=1)), 'An exercise')


class ExercisesTestCase(WgerTestCase):
    """
    Exercise test case
    """

    def search_exercise(self, fail=True):
        """
        Helper function to test searching for exercises
        """

        # 1 hit, "Very cool exercise"
        response = self.client.get(reverse('exercise-search'), {'term': 'cool'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result), 1)
        self.assertEqual(result['suggestions'][0]['value'], 'Very cool exercise')
        self.assertEqual(result['suggestions'][0]['data']['id'], 2)
        self.assertEqual(result['suggestions'][0]['data']['category'], 'Another category')
        self.assertEqual(result['suggestions'][0]['data']['image'], None)
        self.assertEqual(result['suggestions'][0]['data']['image_thumbnail'], None)

        # 0 hits, "Pending exercise"
        response = self.client.get(reverse('exercise-search'), {'term': 'Foobar'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(result['suggestions']), 0)

    def test_search_exercise_anonymous(self):
        """
        Test deleting an exercise by an anonymous user
        """

        self.search_exercise()

    def test_search_exercise_logged_in(self):
        """
        Test deleting an exercise by a logged-in user
        """

        self.user_login('test')
        self.search_exercise()

    def test_exercise_records_historical_data(self):
        """
        Test that changing exercise details generates a historical record
        """
        exercise = Exercise.objects.get(pk=2)
        self.assertEqual(len(exercise.history.all()), 0)

        exercise.name = 'Very cool exercise 2'
        exercise.description = 'New description'
        exercise.exercise_base.muscles_secondary.add(Muscle.objects.get(pk=2))
        exercise.save()

        exercise = Exercise.objects.get(pk=2)
        self.assertEqual(len(exercise.history.all()), 1)


class MuscleTemplateTagTest(WgerTestCase):
    def test_render_main_muscles(self):
        """
        Test that the tag renders only the main muscles
        """

        context = Context({'muscles': Muscle.objects.get(pk=2)})
        template = Template('{% load wger_extras %}{% render_muscles muscles %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/main/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/', rendered_template)
        self.assertIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_main_muscles_empty_secondary(self):
        """
        Test that the tag works when giben main muscles and empty secondary ones
        """

        context = Context({'muscles': Muscle.objects.get(pk=2), 'muscles_sec': []})
        template = Template('{% load wger_extras %}{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/main/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/', rendered_template)
        self.assertIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_secondary_muscles(self):
        """
        Test that the tag renders only the secondary muscles
        """

        context = Context({'muscles': Muscle.objects.get(pk=1)})
        template = Template('{% load wger_extras %}{% render_muscles muscles_sec=muscles %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/secondary/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/main/', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)

    def test_render_secondary_muscles_empty_primary(self):
        """
        Test that the tag works when given secondary muscles and empty main ones
        """

        context = Context({'muscles_sec': Muscle.objects.get(pk=1), 'muscles': []})
        template = Template('{% load wger_extras %}{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/secondary/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/main/', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)

    def test_render_secondary_muscles_list(self):
        """
        Test that the tag works when given a list for secondary muscles and empty main ones
        """

        context = Context({'muscles_sec': Muscle.objects.filter(is_front=True), 'muscles': []})
        template = Template('{% load wger_extras %}{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/secondary/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/muscle-3.svg', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)
        self.assertNotIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_muscle_list(self):
        """
        Test that the tag works when given a list for main and secondary muscles
        """

        context = Context(
            {
                'muscles_sec': Muscle.objects.filter(id__in=[5, 6]),
                'muscles': Muscle.objects.filter(id__in=[1, 4]),
            }
        )
        template = Template('{% load wger_extras %}{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/main/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/main/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/main/muscle-3.svg', rendered_template)
        self.assertIn('images/muscles/main/muscle-4.svg', rendered_template)
        self.assertIn('images/muscles/secondary/muscle-5.svg', rendered_template)
        self.assertIn('images/muscles/secondary/muscle-6.svg', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)
        self.assertNotIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_empty(self):
        """
        Test that the tag works when given empty input
        """

        context = Context({'muscles': [], 'muscles_sec': []})
        template = Template('{% load wger_extras %}{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertEqual(rendered_template, '\n\n')

    def test_render_no_parameters(self):
        """
        Test that the tag works when given no parameters
        """

        template = Template('{% load wger_extras %}{% render_muscles %}')
        rendered_template = template.render(Context({}))
        self.assertEqual(rendered_template, '\n\n')


class WorkoutCacheTestCase(WgerTestCase):
    """
    Workout cache test case
    """

    def test_canonical_form_cache_save(self):
        """
        Tests the workout cache when saving
        """
        exercise = Exercise.objects.get(pk=2)
        for setting in exercise.exercise_base.setting_set.all():
            setting.set.exerciseday.training.canonical_representation
            workout_id = setting.set.exerciseday.training_id
            self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

            exercise.save()
            self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))

    def test_canonical_form_cache_delete(self):
        """
        Tests the workout cache when deleting
        """
        exercise = Exercise.objects.get(pk=2)

        workout_ids = []
        for setting in exercise.exercise_base.setting_set.all():
            workout_id = setting.set.exerciseday.training_id
            workout_ids.append(workout_id)
            setting.set.exerciseday.training.canonical_representation
            self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

        exercise.delete()
        for workout_id in workout_ids:
            self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))


# TODO: fix test, all registered users can upload exercises
class ExerciseApiTestCase(
    api_base_test.BaseTestCase, api_base_test.ApiBaseTestCase, api_base_test.ApiGetTestCase
):
    """
    Tests the exercise overview resource
    """

    pk = 1
    resource = Exercise
    private_resource = False
    overview_cached = True


class ExerciseInfoApiTestCase(
    api_base_test.BaseTestCase,
    api_base_test.ApiBaseTestCase,
    api_base_test.ApiGetTestCase,
):
    """
    Tests the exercise info resource
    """

    pk = 1
    private_resource = False
    overview_cached = True

    def get_resource_name(self):
        return 'exerciseinfo'


class ExerciseBaseInfoApiTestCase(
    api_base_test.BaseTestCase,
    api_base_test.ApiBaseTestCase,
    api_base_test.ApiGetTestCase,
):
    """
    Tests the exercise base info resource
    """

    pk = 1
    private_resource = False
    overview_cached = True

    def get_resource_name(self):
        return 'exercisebaseinfo'


class ExerciseCustomApiTestCase(ExerciseCrudApiTestCase):
    pk = 1

    data = {
        'name': 'A new name',
        'description': 'The wild boar is a suid native to much of Eurasia and North Africa',
        'language': 1,
        'exercise_base': 2,
    }

    def get_resource_name(self):
        return 'exercise-translation'

    def test_cant_change_base_id(self):
        """
        Test that it is not possible to change the base id of an existing
        exercise translation.
        """
        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.exercise_base_id, 1)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'exercise_base': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.exercise_base_id, 1)

    def test_cant_change_language(self):
        """
        Test that it is not possible to change the language id of an existing
        exercise translation.
        """
        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.language_id, 2)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.language_id, 2)

    def test_cant_change_license(self):
        """
        Test that it is not possible to change the license of an existing
        exercise translation.
        """
        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, 2)

        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'license': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, 2)

    def test_cant_set_license(self):
        """
        Test that it is not possible to set the license for a newly created
        exercise translation (the license is always set to the default)
        """
        self.data['license'] = 3

        self.authenticate('trainer1')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.license_id, CC_BY_SA_4_ID)

    def test_patch_clean_html(self):
        """
        Test that the description field has its HTML stripped before saving
        """
        description = '<script>alert();</script> The wild boar is a suid native...'
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'description': description})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.description, 'alert(); The wild boar is a suid native...')

    def test_post_only_one_language_per_base(self):
        """
        Test that it's not possible to add a second translation for the same
        base in the same language.
        """
        self.authenticate('trainer1')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, data=self.data)
        self.assertTrue(response.data['non_field_errors'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_existing_language(self):
        """
        Test that it is possible to set the language if it doesn't duplicate a translation
        """
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 1, 'name': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('non_field_errors'))

    def test_edit_only_one_language_per_base(self):
        """
        Test that it's not possible to edit a translation to a second language for the same base
        """
        self.authenticate('trainer1')
        response = self.client.patch(self.url_detail, data={'language': 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['non_field_errors'])

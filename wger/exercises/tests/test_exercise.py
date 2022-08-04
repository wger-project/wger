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
from django.core import mail
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.template import (
    Context,
    Template,
)
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import (
    STATUS_CODES_FAIL,
    WgerDeleteTestCase,
    WgerTestCase,
)
from wger.exercises.models import (
    Exercise,
    ExerciseCategory,
    Muscle,
)
from wger.utils.cache import cache_mapper
from wger.utils.constants import WORKOUT_TAB
from wger.utils.helpers import random_string


class ExerciseRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual("{0}".format(Exercise.objects.get(pk=1)), 'An exercise')


class ExerciseShareButtonTestCase(WgerTestCase):
    """
    Test that the share button is correctly displayed and hidden
    """

    def test_share_button(self):
        exercise = Exercise.objects.get(pk=1)
        url = exercise.get_absolute_url()

        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])


class ExerciseIndexTestCase(WgerTestCase):

    def exercise_index(self, logged_in=True, demo=False, admin=False):
        """
        Tests the exercise overview page
        """

        response = self.client.get(reverse('exercise:exercise:overview'))

        # Page exists
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], WORKOUT_TAB)

        # Correct categories are shown
        category_1 = response.context['bases'][0].category
        self.assertEqual(category_1.id, 1)
        self.assertEqual(category_1.name, "Category")

        category_2 = response.context['bases'][1].category
        self.assertEqual(category_2.id, 2)
        self.assertEqual(category_2.name, "Another category")

        # Correct exercises in the categories
        exercise_1 = response.context['bases'][0].get_exercise()
        exercise_2 = response.context['bases'][1].get_exercise()
        self.assertEqual(exercise_1.id, 81)
        self.assertEqual(exercise_1.name, "Needed for demo user")

        self.assertEqual(exercise_2.id, 1)
        self.assertEqual(exercise_2.name, "An exercise")

    def test_exercise_index_editor(self):
        """
        Tests the exercise overview page as a logged in user with editor rights
        """

        self.user_login('admin')
        self.exercise_index(admin=True)

    def test_exercise_index_non_editor(self):
        """
        Tests the exercise overview page as a logged in user without editor rights
        """

        self.user_login('test')
        self.exercise_index()

    def test_exercise_index_demo_user(self):
        """
        Tests the exercise overview page as a logged in demo user
        """

        self.user_login('demo')
        self.exercise_index(demo=True)

    def test_exercise_index_logged_out(self):
        """
        Tests the exercise overview page as an anonymous (logged out) user
        """

        self.exercise_index(logged_in=False)

    def test_empty_exercise_index(self):
        """
        Test the index when there are no categories
        """
        self.user_login('admin')
        ExerciseCategory.objects.all().delete()
        response = self.client.get(reverse('exercise:exercise:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No categories')


class ExerciseDetailTestCase(WgerTestCase):
    """
    Tests the exercise details page
    """

    def exercise_detail(self, editor=False):
        """
        Tests the exercise details page
        """

        response = self.client.get(reverse('exercise:exercise:view', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)

        # Correct tab is selected
        self.assertEqual(response.context['active_tab'], WORKOUT_TAB)

        # Exercise loaded correct muscles
        exercise_1 = response.context['exercise']
        self.assertEqual(exercise_1.id, 1)

        muscles = exercise_1.exercise_base.muscles.all()
        muscle_1 = muscles[0]
        muscle_2 = muscles[1]

        self.assertEqual(muscle_1.id, 1)
        self.assertEqual(muscle_2.id, 2)

        # Only authorized users see the edit links
        if editor:
            self.assertContains(response, 'Edit')
            self.assertContains(response, 'Delete')
            self.assertContains(response, 'Add new comment')
        else:
            self.assertNotContains(response, 'Edit')
            self.assertNotContains(response, 'Delete')
            self.assertNotContains(response, 'Add new comment')

        # Ensure that non-existent exercises throw a 404.
        response = self.client.get(reverse('exercise:exercise:view', kwargs={'id': 42}))
        self.assertEqual(response.status_code, 404)

    def test_exercise_detail_editor(self):
        """
        Tests the exercise details page as a logged-in user with editor rights
        """

        self.user_login('admin')
        self.exercise_detail(editor=True)

    def test_exercise_detail_non_editor(self):
        """
        Tests the exercise details page as a logged in user without editor rights
        """

        self.user_login('test')
        self.exercise_detail(editor=False)

    def test_exercise_detail_logged_out(self):
        """
        Tests the exercise details page as an anonymous (logged out) user
        """

        self.exercise_detail(editor=False)


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
        response = self.client.get(reverse('exercise-search'), {'term': 'Pending'})
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
        Test deleting an exercise by a logged in user
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


class DeleteExercisesTestCase(WgerDeleteTestCase):
    """
    Exercise test case
    """

    object_class = Exercise
    url = 'exercise:exercise:delete'
    pk = 2
    user_success = 'admin'
    user_fail = 'test'


class ExercisesCacheTestCase(WgerTestCase):
    """
    Exercise cache test case
    """

    def test_exercise_overview(self):
        """
        Test the exercise overview cache is correctly generated on visit
        """
        self.assertFalse(cache.get(make_template_fragment_key('exercise-overview', [2])))
        self.client.get(reverse('exercise:exercise:overview'))
        self.assertTrue(cache.get(make_template_fragment_key('exercise-overview', [2])))

    def test_exercise_detail(self):
        """
        Test that the exercise detail cache is correctly generated on visit
        """

    def test_overview_cache_update(self):
        """
        Test that the template cache for the overview is correctly reseted when
        performing certain operations
        """
        self.assertFalse(cache.get(make_template_fragment_key('muscle-overview', [2])))
        self.assertFalse(cache.get(make_template_fragment_key('muscle-overview-search', [2])))
        self.assertFalse(cache.get(make_template_fragment_key('exercise-overview', [2])))

        self.client.get(reverse('exercise:exercise:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        old_muscle_overview = cache.get(make_template_fragment_key('muscle-overview', [2]))
        old_exercise_overview = cache.get(make_template_fragment_key('exercise-overview', [2]))

        exercise = Exercise.objects.get(pk=2)
        exercise.name = 'Very cool exercise 2'
        exercise.description = 'New description'
        exercise.exercise_base.muscles_secondary.add(Muscle.objects.get(pk=2))
        exercise.save()

        self.assertFalse(cache.get(make_template_fragment_key('muscle-overview', [2])))
        self.assertFalse(cache.get(make_template_fragment_key('exercise-overview', [2])))

        self.client.get(reverse('exercise:exercise:overview'))
        self.client.get(reverse('exercise:muscle:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        new_muscle_overview = cache.get(make_template_fragment_key('muscle-overview', [2]))
        new_exercise_overview = cache.get(make_template_fragment_key('exercise-overview', [2]))

        self.assertNotEqual(old_exercise_overview, new_exercise_overview)
        self.assertNotEqual(old_muscle_overview, new_muscle_overview)

    def test_muscles_cache_update_on_delete(self):
        """
        Test that the template cache for the overview is correctly reset when
        performing certain operations
        """
        self.assertFalse(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))
        self.assertTrue(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))

        muscle = Muscle.objects.get(pk=2)
        muscle.delete()
        self.assertFalse(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))

    def test_muscles_cache_update_on_update(self):
        """
        Test that the template cache for the overview is correctly reset when
        performing certain operations
        """
        self.assertFalse(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))
        self.assertTrue(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))

        muscle = Muscle.objects.get(pk=2)
        muscle.name = 'foo'
        muscle.save()
        self.assertFalse(cache.get(make_template_fragment_key('exercise-detail-muscles', ["2-2"])))


class MuscleTemplateTagTest(WgerTestCase):

    def test_render_main_muscles(self):
        """
        Test that the tag renders only the main muscles
        """

        context = Context({'muscles': Muscle.objects.get(pk=2)})
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/main/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/', rendered_template)
        self.assertIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_main_muscles_empty_secondary(self):
        """
        Test that the tag works when giben main muscles and empty secondary ones
        """

        context = Context({"muscles": Muscle.objects.get(pk=2), "muscles_sec": []})
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/main/muscle-2.svg', rendered_template)
        self.assertNotIn('images/muscles/secondary/', rendered_template)
        self.assertIn('images/muscles/muscular_system_back.svg', rendered_template)

    def test_render_secondary_muscles(self):
        """
        Test that the tag renders only the secondary muscles
        """

        context = Context({'muscles': Muscle.objects.get(pk=1)})
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles_sec=muscles %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/secondary/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/main/', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)

    def test_render_secondary_muscles_empty_primary(self):
        """
        Test that the tag works when given secondary muscles and empty main ones
        """

        context = Context({'muscles_sec': Muscle.objects.get(pk=1), 'muscles': []})
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertIn('images/muscles/secondary/muscle-1.svg', rendered_template)
        self.assertNotIn('images/muscles/main/', rendered_template)
        self.assertIn('images/muscles/muscular_system_front.svg', rendered_template)

    def test_render_secondary_muscles_list(self):
        """
        Test that the tag works when given a list for secondary muscles and empty main ones
        """

        context = Context({'muscles_sec': Muscle.objects.filter(is_front=True), 'muscles': []})
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles muscles_sec %}')
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
                'muscles': Muscle.objects.filter(id__in=[1, 4])
            }
        )
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles muscles_sec %}')
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
        template = Template('{% load wger_extras %}'
                            '{% render_muscles muscles muscles_sec %}')
        rendered_template = template.render(context)
        self.assertEqual(rendered_template, "\n\n")

    def test_render_no_parameters(self):
        """
        Test that the tag works when given no parameters
        """

        template = Template('{% load wger_extras %}'
                            '{% render_muscles %}')
        rendered_template = template.render(Context({}))
        self.assertEqual(rendered_template, "\n\n")


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


class ExerciseCustomApiTestCase(api_base_test.BaseTestCase, ApiBaseTestCase):

    pk = 1

    def get_resource_name(self):
        return 'exercise-translation'

    def test_change_fields(self):
        """
        Test that it is possible to edit the fields of an exercise translation
        """
        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.name, 'An exercise')
        self.assertEqual(exercise.description, 'Lorem ipsum dolor sit amet')

        data = {
            'name': 'A new name',
            'description': 'The wild boar is a suid native to much of Eurasia and North Africa'
        }
        self.get_credentials('trainer1')
        response = self.client.patch(self.url_detail, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.name, 'A new name')
        self.assertEqual(
            exercise.description,
            'The wild boar is a suid native to much of Eurasia and North Africa'
        )

    def test_cant_change_base_id(self):
        """
        Test that it is not possible to change the base id of an existing
        exercise resource.
        """
        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.exercise_base_id, 1)

        self.get_credentials('trainer1')
        response = self.client.patch(self.url_detail, data={'exercise_base': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.exercise_base_id, 1)

    def test_patch_clean_html(self):
        """
        Test that the description field has its HTML stripped before saving
        """

        description = '<script>alert();</script> The wild boar is a suid native...'
        self.get_credentials('test')
        response = self.client.patch(self.url_detail, data={'description': description})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.description, 'alert(); The wild boar is a suid native...')

    def test_post_clean_html(self):
        """
        Test that the description field has its HTML stripped before creating an exercise
        """

        description = '<script>alert();</script> The wild boar is a suid native...'
        self.get_credentials('test')
        response = self.client.patch(self.url_detail, data={'description': description})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        exercise = Exercise.objects.get(pk=self.pk)
        self.assertEqual(exercise.description, 'alert(); The wild boar is a suid native...')

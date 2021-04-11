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
import logging
from decimal import Decimal
from typing import List

# Django
from django.core.cache import cache
from django.urls import (
    reverse,
    reverse_lazy
)

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    STATUS_CODES_FAIL,
    WgerAddTestCase,
    WgerTestCase
)
from wger.exercises.models import Exercise
from wger.manager.models import (
    Day,
    Set,
    Setting
)
from wger.utils.cache import cache_mapper


logger = logging.getLogger(__name__)


class SetAddTestCase(WgerAddTestCase):
    """
    Test adding a set to a day
    """

    object_class = Set
    url = reverse_lazy('manager:set:add', kwargs={'day_pk': 5})
    user_success = 'test'
    user_fail = 'admin'
    data = {'exercise_list': 1,  # Only for mobile version
            'sets': 4,
            'exercise1-TOTAL_FORMS': 4,
            'exercise1-INITIAL_FORMS': 0,
            'exercise1-MAX_NUM_FORMS': 1000,
            'exercise1-0-reps': 10,
            'exercise1-0-repetition_unit': 1,
            'exercise1-0-weight_unit': 1,
            'exercise1-1-reps': 12,
            'exercise1-1-repetition_unit': 1,
            'exercise1-1-weight_unit': 1,
            'exercise1-2-reps': 10,
            'exercise1-2-repetition_unit': 1,
            'exercise1-2-weight_unit': 1,
            'exercise1-3-reps': 12,
            'exercise1-3-repetition_unit': 1,
            'exercise1-3-weight_unit': 1,
            }
    data_ignore = ('exercise1-TOTAL_FORMS',
                   'exercise1-INITIAL_FORMS',
                   'exercise1-MAX_NUM_FORMS',
                   'exercise_list',
                   'exercise1-0-reps',
                   'exercise1-0-repetition_unit',
                   'exercise1-0-weight_unit',
                   'exercise1-1-reps',
                   'exercise1-1-repetition_unit',
                   'exercise1-1-weight_unit',
                   'exercise1-2-reps',
                   'exercise1-2-repetition_unit',
                   'exercise1-2-weight_unit',
                   'exercise1-3-reps',
                   'exercise1-3-repetition_unit',
                   'exercise1-3-weight_unit')

    def test_add_set(self, fail=False):
        """
        Tests adding a set and corresponding settings at the same time
        """

        # POST the data
        self.user_login('test')
        exercises_id = [1, 2]
        post_data = {'exercise_list': 1,  # Only for mobile version
                     'sets': 4,

                     'exercise1-TOTAL_FORMS': 4,
                     'exercise1-INITIAL_FORMS': 0,
                     'exercise1-MAX_NUM_FORMS': 1000,
                     'exercise1-0-reps': 10,
                     'exercise1-0-repetition_unit': 1,
                     'exercise1-0-weight_unit': 1,
                     'exercise1-1-reps': 12,
                     'exercise1-1-repetition_unit': 1,
                     'exercise1-1-weight_unit': 1,
                     'exercise1-2-reps': 10,
                     'exercise1-2-repetition_unit': 1,
                     'exercise1-2-weight_unit': 1,
                     'exercise1-3-reps': 12,
                     'exercise1-3-repetition_unit': 1,
                     'exercise1-3-weight_unit': 1,

                     'exercise2-TOTAL_FORMS': 4,
                     'exercise2-INITIAL_FORMS': 0,
                     'exercise2-MAX_NUM_FORMS': 1000,
                     'exercise2-0-reps': 8,
                     'exercise2-0-repetition_unit': 1,
                     'exercise2-0-weight_unit': 1,
                     'exercise2-1-reps': 10,
                     'exercise2-1-repetition_unit': 2,
                     'exercise2-1-weight_unit': 2,
                     'exercise2-2-reps': 8,
                     'exercise2-2-repetition_unit': 1,
                     'exercise2-2-weight_unit': 1,
                     'exercise2-3-reps': 10,
                     'exercise2-3-repetition_unit': 2,
                     'exercise2-3-weight_unit': 2}
        response = self.client.post(reverse('manager:set:add', kwargs={'day_pk': 5}), post_data)
        self.assertEqual(response.status_code, 302)

        set_obj = Set.objects.get(pk=Set.objects.latest('id').id)
        exercise1 = Exercise.objects.get(pk=1)

        # Check that everything got where it's supposed to
        for exercise in set_obj.exercises:
            self.assertIn(exercise.id, exercises_id)

        settings = Setting.objects.filter(set=set_obj)
        for setting in settings:
            if setting.exercise == exercise1:
                self.assertIn(setting.reps, (10, 12))
            else:
                self.assertIn(setting.reps, (8, 10))


class SetDeleteTestCase(WgerTestCase):
    """
    Tests deleting a set from a workout
    """

    def delete_set(self, fail=True):
        """
        Helper function to test deleting a set from a workout
        """

        # Fetch the overview page
        count_before = Set.objects.count()
        response = self.client.get(reverse('manager:set:delete', kwargs={'pk': 3}))
        count_after = Set.objects.count()

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)
            self.assertRaises(Set.DoesNotExist, Set.objects.get, pk=3)

    def test_delete_set_anonymous(self):
        """
        Tests deleting a set from a workout as an anonymous user
        """

        self.delete_set(fail=True)

    def test_delete_set_owner(self):
        """
        Tests deleting a set from a workout as the owner user
        """

        self.user_login('admin')
        self.delete_set(fail=True)

    def test_delete_set_other(self):
        """
        Tests deleting a set from a workout as a logged user not owning the data
        """

        self.user_login('test')
        self.delete_set(fail=False)


class TestSetOrderTestCase(WgerTestCase):
    """
    Tests that the order of the (existing) sets in a workout is preservead
    when adding new ones
    """

    def add_set(self, exercises_id):
        """
        Helper function that adds a set to a day
        """
        nr_sets = 4
        post_data = {'exercises': exercises_id,
                     'exercise_list': exercises_id[0],  # Only for mobile version,
                     'sets': nr_sets}
        for exercise_id in exercises_id:
            post_data['exercise{0}-TOTAL_FORMS'.format(exercise_id)] = nr_sets
            post_data['exercise{0}-INITIAL_FORMS'.format(exercise_id)] = 0
            post_data['exercise{0}-MAX_NUM_FORMS'.format(exercise_id)] = 1000
            for set_nr in range(0, nr_sets):
                post_data['exercise{0}-{1}-repetition_unit'.format(exercise_id, set_nr)] = 1
                post_data['exercise{0}-{1}-weight_unit'.format(exercise_id, set_nr)] = 1
                post_data['exercise{0}-{1}-reps'.format(exercise_id, set_nr)] = 8

        response = self.client.post(reverse('manager:set:add', kwargs={'day_pk': 5}),
                                    post_data)

        return response

    def get_order(self):
        """
        Helper function that reads the order of the the sets in a day
        """

        day = Day.objects.get(pk=5)
        order = ()

        for day_set in day.set_set.select_related():
            order += (day_set.id,)

        return order

    def test_set_order(self, logged_in=False):
        """
        Helper function that add some sets and checks the order
        """

        self.user_login('test')
        orig = self.get_order()
        exercises = (1, 2, 3, 81, 84, 91, 111)

        for i in range(0, 7):
            self.add_set([exercises[i]])
            prev = self.get_order()
            orig += (i + 4,)
            self.assertEqual(orig, prev)


class TestSetAddFormset(WgerTestCase):
    """
    Tests the functionality of the formset mini-view that is used in the add
    set page
    """

    def get_formset(self):
        """
        Helper function
        """
        exercise = Exercise.objects.get(pk=1)
        response = self.client.get(reverse('manager:set:get-formset',
                                   kwargs={'exercise_pk': 1, 'reps': 4}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['exercise'], exercise)
        self.assertTrue(response.context['formset'])

    def test_get_formset_logged_in(self):
        """
        Tests the formset view as an authorized user
        """

        self.user_login('test')
        self.get_formset()


class SetEditEditTestCase(WgerTestCase):
    """
    Tests editing a set
    """

    def edit_set(self, fail=False):
        """
        Helper function
        """

        # Fetch the edit page
        response = self.client.get(reverse('manager:set:edit', kwargs={'pk': 3}))
        entry_before = Set.objects.get(pk=3)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
        else:
            self.assertEqual(response.status_code, 200)

        # Try to edit the object
        response = self.client.post(reverse('manager:set:edit', kwargs={'pk': 3}),
                                    {'exercise2-TOTAL_FORMS': 1,
                                     'exercise2-INITIAL_FORMS': 1,
                                     'exercise2-MAX_NUM_FORMS': 1,
                                     'exercise2-MIN_NUM_FORMS': 1,
                                     'exercise2-0-reps': 5,
                                     'exercise2-0-id': 3,
                                     'exercise2-0-repetition_unit': 2,
                                     'exercise2-0-weight_unit': 3,
                                     'exercise2-0-rir': '1.5'})

        entry_after = Set.objects.get(pk=3)

        # Check the results
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertEqual(entry_before, entry_after)

        else:
            self.assertEqual(response.status_code, 302)

            # The page we are redirected to doesn't trigger an error
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)

            # Setting was updated
            setting = Setting.objects.get(pk=3)
            self.assertEqual(setting.reps, 5)
            self.assertEqual(setting.repetition_unit_id, 2)
            self.assertEqual(setting.weight_unit_id, 3)
            self.assertEqual(setting.rir, '1.5')

        self.post_test_hook()

    def test_edit_set_authorized(self):
        """
        Tests editing the object as an authorized user
        """

        self.user_login('admin')
        self.edit_set(fail=True)

    def test_edit_set_other(self):
        """
        Tests editing the object as an unauthorized, logged in user
        """

        self.user_login('test')
        self.edit_set(fail=False)


class SetWorkoutCacheTestCase(WgerTestCase):
    """
    Workout cache test case
    """

    def test_canonical_form_cache_save(self):
        """
        Tests the workout cache when saving
        """
        set = Set.objects.get(pk=1)
        set.exerciseday.training.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(set.exerciseday.training_id)))

        set.save()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(set.exerciseday.training_id)))

    def test_canonical_form_cache_delete(self):
        """
        Tests the workout cache when deleting
        """
        set = Set.objects.get(pk=1)
        set.exerciseday.training.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(set.exerciseday.training_id)))

        set.delete()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(set.exerciseday.training_id)))


class SettingWorkoutCacheTestCase(WgerTestCase):
    """
    Workout cache test case
    """

    def test_canonical_form_cache_save(self):
        """
        Tests the workout cache when saving
        """
        setting = Setting.objects.get(pk=1)
        workout_id = setting.set.exerciseday.training_id
        setting.set.exerciseday.training.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

        setting.save()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))

    def test_canonical_form_cache_delete(self):
        """
        Tests the workout cache when deleting
        """
        setting = Setting.objects.get(pk=1)
        workout_id = setting.set.exerciseday.training_id
        setting.set.exerciseday.training.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

        setting.delete()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))


class SetSmartReprTestCase(WgerTestCase):
    """Tests the "smart text representation" for sets"""

    def test_smart_repr_one_setting(self):
        """
        Tests the representation with one setting
        """
        set_obj = Set.objects.get(pk=1)

        setting_text = set_obj.reps_smart_text(set_obj.exercises[0])
        self.assertEqual(setting_text, '2 × 8 (3 RiR)')

    def test_smart_repr_custom_setting(self):
        """
        Tests the representation with several settings
        """
        set_obj = Set(exerciseday_id=1, order=1, sets=4)
        set_obj.save()
        setting1 = Setting(set=set_obj,
                           exercise_id=1,
                           repetition_unit_id=1,
                           reps=8,
                           weight=Decimal(90),
                           weight_unit_id=1,
                           rir='3',
                           order=1)
        setting1.save()
        setting2 = Setting(set=set_obj,
                           exercise_id=1,
                           repetition_unit_id=1,
                           reps=10,
                           weight=Decimal(80),
                           weight_unit_id=1,
                           rir='2.5',
                           order=2)
        setting2.save()
        setting3 = Setting(set=set_obj,
                           exercise_id=1,
                           repetition_unit_id=1,
                           reps=10,
                           weight=Decimal(80),
                           weight_unit_id=1,
                           rir='2',
                           order=3)
        setting3.save()
        setting4 = Setting(set=set_obj,
                           exercise_id=1,
                           repetition_unit_id=1,
                           reps=12,
                           weight=Decimal(80),
                           weight_unit_id=1,
                           rir='1',
                           order=4)
        setting4.save()

        setting_text = set_obj.reps_smart_text(Exercise.objects.get(pk=1))
        self.assertEqual(setting_text,
                         '8 (90 kg, 3 RiR) – 10 (80 kg, 2.5 RiR) – '
                         '10 (80 kg, 2 RiR) – 12 (80 kg, 1 RiR)')

    def test_synthetic_settings(self):
        set_obj = Set(exerciseday_id=1, order=1, sets=4)
        set_obj.save()
        setting1 = Setting(set=set_obj,
                           exercise_id=1,
                           repetition_unit_id=1,
                           reps=8,
                           weight=Decimal(90),
                           weight_unit_id=1,
                           rir='3',
                           order=1)
        setting1.save()
        setting2 = Setting(set=set_obj,
                           exercise_id=3,
                           repetition_unit_id=1,
                           reps=10,
                           weight=Decimal(80),
                           weight_unit_id=1,
                           rir='2.5',
                           order=2)
        setting2.save()
        settings: List[Setting] = set_obj.compute_settings

        # Check that there are 2 x 4 entries (2 Exercises x 4 Sets)
        self.assertEqual(len(settings), 8)

        # Check interleaved settings
        for i in range(0, len(settings)):
            if (i % 2) == 0:
                self.assertEqual(settings[i].exercise_id, 1)
                self.assertEqual(settings[i].reps, 8)
                self.assertEqual(settings[i].weight, Decimal(90))
                self.assertEqual(settings[i].rir, '3')
            else:
                self.assertEqual(settings[i].exercise_id, 3)
                self.assertEqual(settings[i].reps, 10)
                self.assertEqual(settings[i].weight, Decimal(80))
                self.assertEqual(settings[i].rir, '2.5')


class SetApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the set overview resource
    """
    pk = 3
    resource = Set
    private_resource = True
    data = {'exerciseday': 5,
            'sets': 4}

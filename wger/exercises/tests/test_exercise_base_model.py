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
import datetime

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Exercise,
    ExerciseBase,
)


class ExerciseBaseTranslationHandlingTestCase(WgerTestCase):
    """
    Test the logic used to handle bases without translations
    """

    def setUp(self):
        super().setUp()
        Exercise.objects.get(pk=1).delete()
        Exercise.objects.get(pk=5).delete()

    def test_managers(self):
        self.assertEqual(ExerciseBase.translations.all().count(), 7)
        self.assertEqual(ExerciseBase.no_translations.all().count(), 1)
        self.assertEqual(ExerciseBase.objects.all().count(), 8)

    def test_checks(self):
        out = ExerciseBase.check()
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].id, 'wger.W002')


class ExerciseBaseModelTestCase(WgerTestCase):
    """
    Test custom model logic
    """

    exercise: ExerciseBase

    def setUp(self):
        super().setUp()
        self.exercise = ExerciseBase.objects.get(pk=1)

    def test_access_date(self):
        utc = datetime.timezone.utc
        self.assertEqual(
            self.exercise.last_update_global, datetime.datetime(2023, 8, 9, 23, 0, tzinfo=utc)
        )

        self.assertEqual(
            self.exercise.last_update, datetime.datetime(2020, 11, 1, 21, 10, tzinfo=utc)
        )

        self.assertEqual(
            max(*[translation.last_update for translation in self.exercise.exercises.all()]),
            datetime.datetime(2022, 2, 2, 5, 45, 11, tzinfo=utc),
        )

        self.assertEqual(
            max(*[video.last_update for video in self.exercise.exerciseimage_set.all()]),
            datetime.datetime(2023, 8, 9, 23, 0, tzinfo=utc),
        )

    def test_exercise_en(self):
        translation = self.exercise.get_translation()
        self.assertEqual(translation.language.short_name, 'en')

    def test_get_exercise_fr(self):
        translation = self.exercise.get_translation('fr')
        self.assertEqual(translation.language.short_name, 'fr')

    def test_get_exercise_unknown(self):
        translation = self.exercise.get_translation('kg')
        self.assertEqual(translation.language.short_name, 'en')

    def test_get_languages(self):
        languages = self.exercise.languages
        self.assertEqual(languages[0].short_name, 'en')
        self.assertEqual(languages[1].short_name, 'fr')

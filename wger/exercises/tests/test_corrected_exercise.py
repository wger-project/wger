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
from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.exercises.models import Exercise


class ExercisesCorrectionTestCase(WorkoutManagerTestCase):
    '''
    Tests correcting an existing exercise
    '''

    def correct_exercise(self, fail=True):
        '''
        Helper function
        '''
        description = 'a nice, long and accurate description for the exercise'
        response = self.client.post(reverse('exercise:exercise:correct', kwargs={'pk': 1}),
                                    {'category': 3,
                                     'name_original': 'my test exercise',
                                     'license': 2,
                                     'description': description,
                                     'muscles': [3]})

        if fail:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertEqual(response.status_code, 302)
            new_location = response['Location']
            response = self.client.get(new_location)
            self.assertEqual(response.status_code, 200)

        # Submitting a correction doesn't change the original exercise
        exercise = Exercise.objects.get(pk=1)
        self.assertEqual(exercise.name, 'An exercise')
        self.assertEqual(exercise.description, '')
        self.assertEqual(exercise.category_id, 2)
        self.assertEqual(exercise.language_id, 1)
        self.assertEqual([i.pk for i in exercise.muscles.all()], [1, 2])
        self.assertEqual([i.pk for i in exercise.muscles_secondary.all()], [3])

        # Check the notification email
        if fail:
            self.assertEqual(len(mail.outbox), 0)
        else:
            self.assertEqual(len(mail.outbox), 1)

    def test_correct_exercise_logged_in_user(self):
        '''
        Tests correcting an existing exercise as a logged in user
        '''
        self.user_login('test')
        self.correct_exercise(fail=False)

    def test_correct_exercise_guest_user(self):
        '''
        Tests correcting an existing exercise as a guest user
        '''
        self.user_login('demo')
        self.correct_exercise(fail=True)

    def test_correct_exercise_anonymous(self):
        '''
        Tests correcting an existing exercise as an anonymous user
        '''
        self.correct_exercise(fail=True)

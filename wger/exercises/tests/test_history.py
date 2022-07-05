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

# Third Party
from actstream import action as actstream_action

# wger
from wger.core.tests.base_testcase import (
    WgerTestCase,
)
from wger.exercises.models import (
    Exercise,
)
from wger.exercises.views.helper import StreamVerbs
from django.contrib.auth.models import User


class ExerciseHistoryControl(WgerTestCase):
    """
    Test the history control view
    """

    def test_admin_control_view(self):
        """
        Test that admin control page is accessible
        """
        self.user_login()

        exercise = Exercise.objects.get(pk=2)

        exercise.save()
        exercise.name = 'Very cool exercise!'
        exercise.save()

        exercise = Exercise.objects.get(pk=2)

        most_recent_history = exercise.history.order_by('history_date').last()

        user = User.objects.all().first()

        actstream_action.send(
            user,
            verb=StreamVerbs.UPDATED.value,
            action_object=exercise,
            data={
                'history_id': most_recent_history.history_id,
            }
        )

        response = self.client.get(reverse('exercise:history:admin-control'))

        self.assertEqual(StreamVerbs.__members__, response.context['modes'])
        self.assertEqual(1, len(response.context['context']))

    def test_admin_revert_view(self):
        """
        Test that revert is accessible
        """
        self.user_login()

        exercise = Exercise.objects.get(pk=2)

        exercise.save()
        exercise.description = 'Very cool exercise!'
        exercise.save()

        exercise = Exercise.objects.get(pk=2)

        most_recent_history = exercise.history.order_by('history_date').last()

        user = User.objects.all().first()

        actstream_action.send(
            user,
            verb=StreamVerbs.UPDATED.value,
            action_object=exercise,
            data={
                'history_id': most_recent_history.history_id,
            }
        )

        self.client.get(reverse('exercise:history:history-revert',
                        kwargs={'pk': most_recent_history.history_id}))

        exercise = Exercise.objects.get(pk=2)

        self.assertNotEqual(exercise.description, 'Very cool exercise!')

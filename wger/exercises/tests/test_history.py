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
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

# Third Party
from actstream import action as actstream_action

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import Translation
from wger.exercises.views.helper import StreamVerbs


class ExerciseHistoryControl(WgerTestCase):
    """
    Test the history control view
    """

    def test_admin_control_view(self):
        """
        Test that admin control page is accessible
        """
        self.user_login()

        translation = Translation.objects.get(pk=2)

        translation.save()
        translation.name = 'Very cool exercise!'
        translation.save()

        translation = Translation.objects.get(pk=2)
        actstream_action.send(
            User.objects.all().first(),
            verb=StreamVerbs.UPDATED.value,
            action_object=translation,
        )

        response = self.client.get(reverse('exercise:history:overview'))

        self.assertEqual(StreamVerbs.__members__, response.context['verbs'])
        self.assertEqual(1, len(response.context['context']))

    def test_admin_revert_view(self):
        """
        Test that revert is accessible
        """
        self.user_login()

        translation = Translation.objects.get(pk=2)
        translation.description = 'Boring exercise'
        translation.save()

        most_recent_history = translation.history.order_by('history_date').last()
        translation.description = 'Very cool exercise!'
        translation.save()

        self.client.get(
            reverse(
                'exercise:history:revert',
                kwargs={
                    'history_pk': most_recent_history.history_id,
                    'content_type_id': ContentType.objects.get_for_model(translation).id,
                },
            )
        )

        translation = Translation.objects.get(pk=2)
        self.assertEqual(translation.description, 'Boring exercise')

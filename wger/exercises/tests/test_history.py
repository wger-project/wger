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
from datetime import timedelta

# Django
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

# Third Party
from actstream import action as actstream_action
from actstream.models import Action

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Alias,
    Translation,
)
from wger.exercises.views.helper import StreamVerbs
from wger.exercises.views.history import PAGE_SIZE


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
        Test that revert is accessible via POST
        """
        self.user_login()

        translation = Translation.objects.get(pk=2)
        translation.description = 'Boring exercise'
        translation.save()

        most_recent_history = translation.history.order_by('history_date').last()
        translation.description = 'Very cool exercise!'
        translation.save()

        response = self.client.post(
            reverse(
                'exercise:history:revert',
                kwargs={
                    'history_pk': most_recent_history.history_id,
                    'content_type_id': ContentType.objects.get_for_model(translation).id,
                },
            )
        )

        self.assertEqual(response.status_code, 302)
        translation = Translation.objects.get(pk=2)
        self.assertEqual(translation.description, 'Boring exercise')

    def test_admin_revert_rejects_get(self):
        """
        Revert is state-changing and must not be reachable via GET; only POST
        with a CSRF token is allowed.
        """
        self.user_login()

        translation = Translation.objects.get(pk=2)
        translation.description = 'Boring exercise'
        translation.save()
        most_recent_history = translation.history.order_by('history_date').last()
        translation.description = 'Very cool exercise!'
        translation.save()

        response = self.client.get(
            reverse(
                'exercise:history:revert',
                kwargs={
                    'history_pk': most_recent_history.history_id,
                    'content_type_id': ContentType.objects.get_for_model(translation).id,
                },
            )
        )

        self.assertEqual(response.status_code, 405)
        translation = Translation.objects.get(pk=2)
        self.assertEqual(translation.description, 'Very cool exercise!')


class ExerciseHistoryControlExtras(WgerTestCase):
    """
    Tests for pagination, filters and contributor flagging on the history
    control view.
    """

    def setUp(self):
        super().setUp()
        self.user_login()
        self.user = User.objects.get(username='admin')

    def _make_action(self, target, verb=None):
        verb = verb or StreamVerbs.UPDATED.value
        actstream_action.send(self.user, verb=verb, action_object=target)

    def test_deleted_action_object_does_not_crash(self):
        """
        If the action_object referenced by an Action no longer resolves to a
        live row, the view must still render

        actstream's ``registry.register`` attaches a GenericRelation that
        cascades when the action_object is deleted, so we simulate a dangling
        reference by pointing the action_object FK to a non-existent pk.
        """
        translation = Translation.objects.get(pk=2)
        self._make_action(translation)

        action = Action.objects.first()
        action.action_object_object_id = 999_999
        action.save()

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Object was deleted')

    def test_pagination(self):
        """
        Verify the paginator splits the action stream into pages of PAGE_SIZE.
        """
        translation = Translation.objects.get(pk=2)
        for _ in range(PAGE_SIZE + 5):
            self._make_action(translation)

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context']), PAGE_SIZE)
        self.assertTrue(response.context['is_paginated'])

        response_page2 = self.client.get(reverse('exercise:history:overview') + '?page=2')
        self.assertEqual(response_page2.status_code, 200)
        self.assertEqual(len(response_page2.context['context']), 5)

    def test_filter_by_user(self):
        """
        The ``user`` GET parameter filters by actor username (case-insensitive
        substring match).
        """
        other_user = User.objects.get(username='test')
        translation = Translation.objects.get(pk=2)

        actstream_action.send(self.user, verb=StreamVerbs.UPDATED.value, action_object=translation)
        actstream_action.send(other_user, verb=StreamVerbs.UPDATED.value, action_object=translation)

        response = self.client.get(reverse('exercise:history:overview') + '?user=test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context']), 1)
        self.assertEqual(response.context['context'][0]['stream'].actor, other_user)

    def test_filter_by_model_type(self):
        """
        Filtering by ``model_type`` should restrict to the matching content
        type only.
        """
        translation = Translation.objects.get(pk=2)
        alias = Alias.objects.create(translation=translation, alias='filter-test')

        self._make_action(translation)
        self._make_action(alias)

        response = self.client.get(reverse('exercise:history:overview') + '?model_type=alias')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context']), 1)
        self.assertEqual(response.context['context'][0]['model_key'], 'alias')

    def test_new_contributor_flag(self):
        """
        Actors whose account is younger than 60 days are flagged so admins
        can review them more carefully.
        """

        new_user = User.objects.create_user(username='newbie', password='pw')
        new_user.date_joined = timezone.now() - timedelta(days=3)
        new_user.save()

        translation = Translation.objects.get(pk=2)
        actstream_action.send(new_user, verb=StreamVerbs.UPDATED.value, action_object=translation)
        actstream_action.send(self.user, verb=StreamVerbs.UPDATED.value, action_object=translation)

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)

        new_flagged = [e for e in response.context['context'] if e['is_new_contributor']]
        self.assertEqual(len(new_flagged), 1)
        self.assertEqual(new_flagged[0]['stream'].actor, new_user)

    def test_stats_header(self):
        translation = Translation.objects.get(pk=2)
        self._make_action(translation)

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context['stats']['last_24h'], 1)
        self.assertGreaterEqual(response.context['stats']['last_7d'], 1)
        self.assertGreaterEqual(response.context['stats']['last_30d'], 1)

    def test_deleted_event_surfaces_without_action_object(self):
        """
        A DELETED actstream event has no action_object (the original is gone)
        but must still appear in the feed with model_key picked up from
        ``data.model_type``.
        """
        actstream_action.send(
            self.user,
            verb=StreamVerbs.DELETED.value,
            deleted_uuid='ae3328ba-9a35-4731-bc23-5da50720c5aa',
            deleted_repr='Some deleted exercise',
            model_type='exercise',
        )

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)

        deleted_events = [
            e for e in response.context['context'] if e['verb'] == StreamVerbs.DELETED.value
        ]
        self.assertEqual(len(deleted_events), 1)
        self.assertEqual(deleted_events[0]['model_key'], 'exercise')
        self.assertContains(response, 'Some deleted exercise')

    def test_merged_event_links_to_replacement(self):
        """
        A MERGED event keeps its action_object pointing at the surviving
        replacement exercise.
        """
        replacement = Translation.objects.get(pk=2).exercise

        actstream_action.send(
            self.user,
            verb=StreamVerbs.MERGED.value,
            action_object=replacement,
            deleted_uuid='ae3328ba-9a35-4731-bc23-5da50720c5aa',
            deleted_repr='Duplicate exercise',
            transfer_media=True,
            transfer_translations=False,
        )

        response = self.client.get(reverse('exercise:history:overview'))
        self.assertEqual(response.status_code, 200)

        merged_events = [
            e for e in response.context['context'] if e['verb'] == StreamVerbs.MERGED.value
        ]
        self.assertEqual(len(merged_events), 1)
        self.assertEqual(merged_events[0]['stream'].action_object, replacement)
        self.assertContains(response, 'Duplicate exercise')

    def test_filter_by_verb_deleted(self):
        """The verb dropdown can isolate DELETED events."""
        translation = Translation.objects.get(pk=2)
        self._make_action(translation, verb=StreamVerbs.UPDATED.value)
        actstream_action.send(
            self.user,
            verb=StreamVerbs.DELETED.value,
            deleted_uuid='ae3328ba-9a35-4731-bc23-5da50720c5aa',
            deleted_repr='Gone',
            model_type='exercise',
        )

        response = self.client.get(reverse('exercise:history:overview') + '?verb=deleted')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context']), 1)
        self.assertEqual(
            response.context['context'][0]['verb'],
            StreamVerbs.DELETED.value,
        )

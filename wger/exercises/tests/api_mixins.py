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
from django.contrib.contenttypes.models import ContentType

# Third Party
from actstream.models import Action
from rest_framework import status

# wger
from wger.exercises.views.helper import StreamVerbs


class _ActstreamMixinBase:
    """
    Common helpers for the actstream-event mixins.

    The model whose ContentType the emitted events reference defaults to
    ``self.resource`` (already set on the standard API test cases) and can be
    overridden via ``actstream_model`` when the two diverge.
    """

    actstream_model = None

    def _actstream_model(self):
        return self.actstream_model or self.resource

    def _count_actions(self, verb):
        ct = ContentType.objects.get_for_model(self._actstream_model())
        return Action.objects.filter(
            verb=verb,
            action_object_content_type=ct,
        ).count()


class ActstreamCreateMixin(_ActstreamMixinBase):
    """POSTing ``self.data`` to ``self.url`` emits a CREATED actstream event."""

    def test_actstream_event_on_create(self):
        self.authenticate('admin')
        before = self._count_actions(StreamVerbs.CREATED.value)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertEqual(self._count_actions(StreamVerbs.CREATED.value), before + 1)


class ActstreamUpdateMixin(_ActstreamMixinBase):
    """PATCHing ``self.data`` to ``self.url_detail`` emits an UPDATED event."""

    def test_actstream_event_on_update(self):
        self.authenticate('admin')
        before = self._count_actions(StreamVerbs.UPDATED.value)
        response = self.client.patch(self.url_detail, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(self._count_actions(StreamVerbs.UPDATED.value), before + 1)


class ActstreamApiMixin(ActstreamCreateMixin, ActstreamUpdateMixin):
    """Covers both create and update — for endpoints supporting POST + PATCH."""

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

    patch_format = 'json'
    """Resources holding a file only parse multipart, those set 'multipart'."""

    def test_actstream_event_on_update(self):
        self.authenticate('admin')
        before = self._count_actions(StreamVerbs.UPDATED.value)
        response = self.client.patch(self.url_detail, data=self.data, format=self.patch_format)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(self._count_actions(StreamVerbs.UPDATED.value), before + 1)


class ActstreamApiMixin(ActstreamCreateMixin, ActstreamUpdateMixin):
    """Covers both create and update — for endpoints supporting POST + PATCH."""


class LicenseAuthorCreateMixin:
    """POSTing ``self.data`` without an author stores the username as license author."""

    def _post_with_author(self, **author):
        self.authenticate('admin')
        response = self.client.post(self.url, data={**self.data, **author})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        return self.resource.objects.get(pk=response.json()['id'])

    def test_license_author_defaults_to_username_on_create(self):
        self.assertEqual(self._post_with_author().license_author, 'admin')

    def test_empty_license_author_becomes_username_on_create(self):
        self.assertEqual(self._post_with_author(license_author='').license_author, 'admin')

    def test_license_author_is_kept_on_create(self):
        obj = self._post_with_author(license_author='Jane Doe')
        self.assertEqual(obj.license_author, 'Jane Doe')


class LicenseAuthorUpdateMixin:
    """PATCHing an empty author stores the username, omitting it keeps the stored one."""

    patch_format = 'json'

    def test_empty_license_author_becomes_username_on_update(self):
        self.authenticate('admin')
        response = self.client.patch(
            self.url_detail,
            data={'license_author': ''},
            format=self.patch_format,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(self.resource.objects.get(pk=self.pk).license_author, 'admin')

    def test_license_author_unchanged_on_update_without_it(self):
        self.resource.objects.filter(pk=self.pk).update(license_author='Jane Doe')
        self.authenticate('admin')
        response = self.client.patch(self.url_detail, data=self.data, format=self.patch_format)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertEqual(self.resource.objects.get(pk=self.pk).license_author, 'Jane Doe')


class LicenseAuthorEditorMixin:
    """PATCHing without a non-empty author stores the editor, a sent author is kept."""

    def _patch_author(self, data):
        self.resource.objects.filter(pk=self.pk).update(license_author='Jane Doe')
        self.authenticate('admin')
        response = self.client.patch(self.url_detail, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        return self.resource.objects.get(pk=self.pk).license_author

    def test_editor_becomes_license_author_on_update(self):
        self.assertEqual(self._patch_author(self.data), 'admin')

    def test_empty_license_author_becomes_editor_on_update(self):
        self.assertEqual(self._patch_author({**self.data, 'license_author': ''}), 'admin')

    def test_license_author_is_kept_on_update(self):
        self.assertEqual(self._patch_author({**self.data, 'license_author': 'Max'}), 'Max')


class LicenseAuthorApiMixin(LicenseAuthorCreateMixin, LicenseAuthorEditorMixin):
    """Create and editor credit, for exercises and translations (POST + PATCH)."""

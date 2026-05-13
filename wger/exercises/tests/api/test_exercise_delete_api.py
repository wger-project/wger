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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from actstream.models import Action
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import (
    Exercise,
    Translation,
)
from wger.exercises.models.image import ExerciseImage
from wger.exercises.models.video import ExerciseVideo
from wger.exercises.views.helper import StreamVerbs


class ExerciseDeleteApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the DELETE endpoint of the exercise API, in particular the optional
    ``replaced_by``, ``transfer_media`` and ``transfer_translations`` query
    parameters.
    """

    # Source has 2 images, 2 videos, translations in lang 2 and lang 3.
    # Target has 1 image, 1 video, translation in lang 2.
    source_pk = 1
    target_pk = 2
    target_uuid = 'ae3328ba-9a35-4731-bc23-5da50720c5aa'

    def url(self):
        return f'/api/v2/exercise/{self.source_pk}/'

    def test_delete_without_replacement_cascades(self):
        """Without replace_by, related media and translations are dropped."""
        self.authenticate('admin')

        response = self.client.delete(self.url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Exercise.objects.filter(pk=self.source_pk).exists())
        self.assertEqual(ExerciseImage.objects.filter(exercise_id=self.source_pk).count(), 0)
        self.assertEqual(ExerciseVideo.objects.filter(exercise_id=self.source_pk).count(), 0)

    def test_delete_with_replacement_no_transfer_flags(self):
        """
        With replace_by but no transfer flags, media and translations are
        cascade-deleted; only routine and log references move.
        """
        self.authenticate('admin')

        response = self.client.delete(f'{self.url()}?replaced_by={self.target_uuid}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        target = Exercise.objects.get(pk=self.target_pk)
        self.assertEqual(target.exerciseimage_set.count(), 1)
        self.assertEqual(target.exercisevideo_set.count(), 1)
        self.assertEqual(set(target.translations.values_list('language_id', flat=True)), {2})

    def test_delete_with_transfer_media(self):
        """transfer_media moves both images and videos to the replacement."""
        self.authenticate('admin')

        response = self.client.delete(f'{self.url()}?replaced_by={self.target_uuid}&transfer_media')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        target = Exercise.objects.get(pk=self.target_pk)
        self.assertEqual(target.exerciseimage_set.count(), 3)
        self.assertEqual(target.exercisevideo_set.count(), 3)

    def test_delete_with_transfer_translations(self):
        """
        transfer_translations moves translations whose language is not yet
        present on the replacement; languages already present are
        cascade-deleted.
        """
        self.authenticate('admin')

        response = self.client.delete(
            f'{self.url()}?replaced_by={self.target_uuid}&transfer_translations'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        target = Exercise.objects.get(pk=self.target_pk)
        self.assertEqual(set(target.translations.values_list('language_id', flat=True)), {2, 3})

        # The lang 3 translation was reassigned (its pk is preserved)
        moved = Translation.objects.get(pk=5)
        self.assertEqual(moved.exercise_id, self.target_pk)

        # The lang 2 translation on the source was cascade-deleted
        self.assertFalse(Translation.objects.filter(pk=1).exists())

    def test_delete_with_both_transfer_flags(self):
        """Both flags can be combined in a single request."""
        self.authenticate('admin')

        response = self.client.delete(
            f'{self.url()}?replaced_by={self.target_uuid}&transfer_media&transfer_translations'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        target = Exercise.objects.get(pk=self.target_pk)
        self.assertEqual(target.exerciseimage_set.count(), 3)
        self.assertEqual(target.exercisevideo_set.count(), 3)
        self.assertEqual(set(target.translations.values_list('language_id', flat=True)), {2, 3})

    def test_delete_transfer_flags_ignored_without_replacement(self):
        """Transfer flags without replace_by have no effect — full cascade."""
        self.authenticate('admin')

        response = self.client.delete(f'{self.url()}?transfer_media&transfer_translations')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Exercise.objects.filter(pk=self.source_pk).exists())
        target = Exercise.objects.get(pk=self.target_pk)
        self.assertEqual(target.exerciseimage_set.count(), 1)
        self.assertEqual(target.exercisevideo_set.count(), 1)

    def test_delete_invalid_replaced_by_is_ignored(self):
        """An invalid UUID in replace_by is silently ignored."""
        self.authenticate('admin')

        response = self.client.delete(f'{self.url()}?replaced_by=not-a-uuid')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Exercise.objects.filter(pk=self.source_pk).exists())

    def test_delete_without_replacement_emits_deleted_event(self):
        """A plain delete fires a DELETED actstream event with the model_type."""
        self.authenticate('admin')

        before = Action.objects.filter(verb=StreamVerbs.DELETED.value).count()
        source = Exercise.objects.get(pk=self.source_pk)
        deleted_uuid = str(source.uuid)
        deleted_repr = str(source)

        response = self.client.delete(self.url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Action.objects.filter(verb=StreamVerbs.DELETED.value).count(),
            before + 1,
        )
        event = Action.objects.filter(verb=StreamVerbs.DELETED.value).latest('timestamp')
        self.assertIsNone(event.action_object)
        self.assertEqual(event.data['deleted_uuid'], deleted_uuid)
        self.assertEqual(event.data['deleted_repr'], deleted_repr)
        self.assertEqual(event.data['model_type'], 'exercise')

    def test_delete_with_replacement_emits_merged_event(self):
        """A delete with replace_by fires a MERGED event pointing at the target."""
        self.authenticate('admin')

        before = Action.objects.filter(verb=StreamVerbs.MERGED.value).count()
        source = Exercise.objects.get(pk=self.source_pk)
        deleted_uuid = str(source.uuid)
        deleted_repr = str(source)

        response = self.client.delete(
            f'{self.url()}?replaced_by={self.target_uuid}&transfer_media&transfer_translations'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Action.objects.filter(verb=StreamVerbs.MERGED.value).count(),
            before + 1,
        )
        event = Action.objects.filter(verb=StreamVerbs.MERGED.value).latest('timestamp')
        self.assertEqual(event.action_object, Exercise.objects.get(pk=self.target_pk))
        self.assertEqual(event.data['deleted_uuid'], deleted_uuid)
        self.assertEqual(event.data['deleted_repr'], deleted_repr)
        self.assertTrue(event.data['transfer_media'])
        self.assertTrue(event.data['transfer_translations'])

    def test_delete_with_invalid_replacement_emits_deleted_event(self):
        """
        An unresolvable replaced_by must fall through to a DELETED event, not
        emit a MERGED one referencing a non-existent target.
        """
        self.authenticate('admin')

        before_deleted = Action.objects.filter(verb=StreamVerbs.DELETED.value).count()
        before_merged = Action.objects.filter(verb=StreamVerbs.MERGED.value).count()

        response = self.client.delete(f'{self.url()}?replaced_by=not-a-uuid')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Action.objects.filter(verb=StreamVerbs.DELETED.value).count(),
            before_deleted + 1,
        )
        self.assertEqual(
            Action.objects.filter(verb=StreamVerbs.MERGED.value).count(),
            before_merged,
        )

    def test_delete_requires_authentication(self):
        """Anonymous users cannot delete exercises."""
        response = self.client.delete(self.url())

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertTrue(Exercise.objects.filter(pk=self.source_pk).exists())

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
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
    delete_testcase_add_methods,
)
from wger.gym.models import UserDocument


class UserDocumentOverviewTest(WgerAccessTestCase):
    """
    Tests accessing the user document overview page
    """

    url = reverse('gym:document:list', kwargs={'user_pk': 14})
    anonymous_fail = True
    user_success = (
        'trainer1',
        'trainer2',
        'trainer3',
    )
    user_fail = (
        'admin',
        'member1',
        'member2',
        'trainer4',
        'manager3',
        'general_manager1',
    )


class AddDocumentTestCase(WgerAddTestCase):
    """
    Tests uploading a new user document
    """

    object_class = UserDocument
    url = reverse('gym:document:add', kwargs={'user_pk': 14})
    fileupload = ['document', 'wger/gym/tests/Wurzelpetersilie.pdf']
    data = {'name': 'Petersilie'}
    data_ignore = ['document']
    user_success = (
        'trainer1',
        'trainer2',
        'trainer3',
    )
    user_fail = (
        'member1',
        'member2',
        'trainer4',
        'manager3',
        'general_manager1',
    )


class EditDocumentTestCase(WgerEditTestCase):
    """
    Tests editing a user document
    """

    pk = 2
    object_class = UserDocument
    url = 'gym:document:edit'
    data = {'name': 'Petersilie'}
    user_success = (
        'trainer1',
        'trainer2',
        'trainer3',
    )
    user_fail = (
        'member1',
        'member2',
        'trainer4',
        'manager3',
        'general_manager1',
    )


class DeleteDocumentTestCase(WgerDeleteTestCase):
    """
    Tests deleting a user document
    """

    pk = 1
    object_class = UserDocument
    url = 'gym:document:delete'
    user_success = (
        'trainer1',
        'trainer2',
        'trainer3',
    )
    user_fail = (
        'admin',
        'member1',
        'member2',
        'trainer4',
        'manager3',
        'general_manager1',
    )



delete_testcase_add_methods(DeleteDocumentTestCase)


class UserDocumentFileValidationTest(WgerTestCase):
    """
    Tests file extension validation on the UserDocument.document field
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')

    def test_valid_file_extension(self):
        """
        A file with an allowed extension (.pdf) should pass full_clean() without errors
        """
        doc = UserDocument(
            user=self.user,
            member=self.user,
            document=SimpleUploadedFile('safe.pdf', b'%PDF-1.4 fake content'),
            original_name='safe.pdf',
        )
        doc.full_clean()

    def test_invalid_file_extension(self):
        """
        A file with a disallowed extension (.txt) should raise a ValidationError
        """
        doc = UserDocument(
            user=self.user,
            member=self.user,
            document=SimpleUploadedFile('malware.txt', b'not allowed content'),
            original_name='malware.txt',
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

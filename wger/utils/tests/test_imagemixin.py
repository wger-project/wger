# Django
from django.test import SimpleTestCase

# wger
from wger.utils.helpers import BaseImageMixin


class ImageMixinTestCase(SimpleTestCase):
    def test_from_json_sets_uuid_and_license(self):
        json_data = {
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'license_title': 'CC0',
            'license_object_url': 'https://license.example/',
            'license_author': 'Author Name',
            'license_author_url': 'https://author.example/',
            'license_derivative_source_url': 'https://source.example/',
        }

        img = BaseImageMixin.from_json(
            connect_to=None,
            retrieved_image=None,
            json_data=json_data,
            generate_uuid=False,
            has_license_information=True,
        )

        self.assertIsInstance(img, BaseImageMixin)
        self.assertEqual(getattr(img, 'uuid'), json_data['uuid'])
        self.assertEqual(img.license_title, json_data['license_title'])
        self.assertEqual(img.license_object_url, json_data['license_object_url'])
        self.assertEqual(img.license_author, json_data['license_author'])
        self.assertEqual(img.license_author_url, json_data['license_author_url'])
        self.assertEqual(
            img.license_derivative_source_url, json_data['license_derivative_source_url']
        )

    def test_from_json_skips_uuid_and_license_when_requested(self):
        json_data = {
            'uuid': 'unused-uuid',
            'license_title': 'Should be skipped',
        }

        img = BaseImageMixin.from_json(
            connect_to=None,
            retrieved_image=None,
            json_data=json_data,
            generate_uuid=True,
            has_license_information=False,
        )

        self.assertIsInstance(img, BaseImageMixin)
        self.assertFalse(hasattr(img, 'uuid'))
        self.assertFalse(hasattr(img, 'license_title'))
        self.assertFalse(hasattr(img, 'license_object_url'))
        self.assertFalse(hasattr(img, 'license_author'))
        self.assertFalse(hasattr(img, 'license_author_url'))
        self.assertFalse(hasattr(img, 'license_derivative_source_url'))

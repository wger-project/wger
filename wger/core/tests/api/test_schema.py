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

# Standard Library
from unittest.mock import patch

# Django
from django.core.cache import cache
from django.test import (
    SimpleTestCase,
    override_settings,
)
from django.utils import translation

# Third Party
from drf_spectacular.generators import SchemaGenerator

# wger
from wger.utils.api_schema import CachedSchemaGenerator
from wger.utils.cache import CacheKeyMapper
from wger.version import get_version_with_git


class SchemaPaginationTestCase(SimpleTestCase):
    """
    The pagination the generated schema promises
    """

    def test_custom_actions_are_not_documented_as_paginated(self):
        """
        A custom action answers with whatever it returns, the pagination of its
        viewset does not apply

        drf-spectacular takes any `many=True` response for a paginated list and
        wraps it in the pagination class of the viewset. Generated clients then
        read `results` out of a bare array and fail, so an action that does not
        paginate has to say so with `pagination_class=None`.
        """
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        paginated = []

        for path, _regex, method, view in generator._get_paths_and_endpoints():
            action = getattr(view, 'action', None)
            handler = getattr(type(view), action, None) if action else None
            if getattr(handler, 'mapping', None) is None:
                continue

            reference = (
                schema['paths'][path][method.lower()]
                .get('responses', {})
                .get('200', {})
                .get('content', {})
                .get('application/json', {})
                .get('schema', {})
                .get('$ref', '')
            )
            if reference.rsplit('/', 1)[-1].startswith('Paginated'):
                paginated.append(f'{method} {path}')

        self.assertEqual(paginated, [])


class SchemaCacheTestCase(SimpleTestCase):
    """
    The caching of the generated schema
    """

    SCHEMA = {'openapi': '3.0.3'}

    def setUp(self):
        cache.clear()

    @patch.object(SchemaGenerator, 'get_schema')
    def test_repeated_requests_reuse_the_cached_schema(self, generate):
        """
        The schema is generated once and served from the cache afterwards
        """
        generate.return_value = self.SCHEMA

        with translation.override('en'):
            first = CachedSchemaGenerator().get_schema(public=True)
            second = CachedSchemaGenerator().get_schema(public=True)

        self.assertEqual(generate.call_count, 1)
        self.assertEqual(first, self.SCHEMA)
        self.assertEqual(second, self.SCHEMA)

    @patch.object(SchemaGenerator, 'get_schema')
    def test_explicit_version_is_not_cached(self, generate):
        """
        A version passed by the caller never reaches a cache key
        """
        generate.return_value = self.SCHEMA

        with translation.override('en'):
            CachedSchemaGenerator(api_version='whatever').get_schema(public=True)
            CachedSchemaGenerator(api_version='whatever').get_schema(public=True)

            self.assertEqual(generate.call_count, 2)
            key = CacheKeyMapper.api_schema_key(get_version_with_git(), 'en')
            self.assertIsNone(cache.get(key))

    @patch.object(SchemaGenerator, 'get_schema')
    def test_unknown_language_is_not_cached(self, generate):
        """
        A language outside of settings.LANGUAGES never reaches a cache key
        """
        generate.return_value = self.SCHEMA

        with translation.override('not-a-language'):
            CachedSchemaGenerator().get_schema(public=True)
            CachedSchemaGenerator().get_schema(public=True)

        self.assertEqual(generate.call_count, 2)

    @override_settings(DEBUG=True)
    @patch.object(SchemaGenerator, 'get_schema')
    def test_debug_always_generates(self, generate):
        """
        During development the schema follows the code, not the version stamp
        """
        generate.return_value = self.SCHEMA

        with translation.override('en'):
            CachedSchemaGenerator().get_schema(public=True)
            CachedSchemaGenerator().get_schema(public=True)

        self.assertEqual(generate.call_count, 2)

    @patch.object(SchemaGenerator, 'get_schema')
    def test_languages_are_cached_separately(self, generate):
        """
        Each language gets its own entry, the descriptions in the schema are
        translated
        """
        generate.return_value = self.SCHEMA

        for language in ('en', 'de'):
            with translation.override(language):
                CachedSchemaGenerator().get_schema(public=True)

        self.assertEqual(generate.call_count, 2)
        for language in ('en', 'de'):
            key = CacheKeyMapper.api_schema_key(get_version_with_git(), language)
            self.assertEqual(cache.get(key), self.SCHEMA)

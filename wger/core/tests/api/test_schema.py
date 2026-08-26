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

# Django
from django.test import SimpleTestCase

# Third Party
from drf_spectacular.generators import SchemaGenerator


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

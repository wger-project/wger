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

"""
Prose for the generated OpenAPI schema, consumed by SPECTACULAR_SETTINGS.

Kept out of the settings module because it is documentation, not configuration,
and it must not import anything from the app registry: the settings are loaded
before the apps are ready.
"""

API_DESCRIPTION = """\
Self hosted FLOSS workout and fitness tracker.

## Authentication

System-wide data such as the exercise database, ingredients and units can be
read without authenticating. Everything tied to a user account needs one of the
following, which are tried in this order:

* `Authorization: Token <key>` with a personal API key. Users create one on the
  API key page of their profile, e.g. `/en/user/api-key`.
* `Authorization: Bearer <token>` with a JWT access token.
* The session cookie, which is what a logged-in browser uses.

## Pagination

List endpoints take `limit` and `offset`, and answer with `count`, `next`,
`previous` and `results`. The default page size is 20 and `limit` is capped
at 999.

`/api/v2/ingredient-sync/` is the exception. It uses cursor pagination so that
syncing the catalogue stays fast no matter how far a client has paginated. That
response carries no `count`, and clients follow `next` instead of picking an
offset.

## Filtering and ordering

Most list endpoints accept filters on a subset of their fields, plus `ordering`
with a field name that can be prefixed with `-` to reverse it. Both are listed
per endpoint.

## Unknown fields are dropped on write

A field that the endpoint does not declare is ignored instead of rejected. Such
a request still answers 200 or 201, and the unknown field simply has no effect,
so check a write against the response body rather than the status code.

## Rate limits

The ingredient endpoints are rate limited because the catalogue holds millions
of rows, and creating exercises is capped as well. Limits count per user for
authenticated callers and per IP otherwise. Exceeding one answers 429.
"""

# Only tags whose purpose is not obvious from the name are described here.
# Tags left out still show up, just without a description.
API_TAGS = [
    {
        'name': 'exercise',
        'description': (
            'The exercise database. Related objects are referenced by ID. This is the '
            'writable endpoint of the two exercise representations.'
        ),
    },
    {
        'name': 'exerciseinfo',
        'description': (
            'The same exercises read-only, with categories, muscles, equipment, images, '
            'videos and translations expanded inline. Meant for external tools and '
            'integrations: one request returns everything, with no IDs left to resolve.'
        ),
    },
    {
        'name': 'ingredient',
        'description': (
            'Nutritional information per ingredient, referencing related objects by ID. '
            'Read-only and rate limited.'
        ),
    },
    {
        'name': 'ingredientinfo',
        'description': (
            'The same ingredients read-only, with language, license, image and weight units '
            'expanded inline. Meant for external tools and integrations: one request returns '
            'everything, with no IDs left to resolve.'
        ),
    },
    {
        'name': 'ingredient-sync',
        'description': (
            'The same data as ingredientinfo, but cursor paginated for mirroring the whole '
            'catalogue. No `count`, and only `next`/`previous` rather than arbitrary '
            'offsets. Combine with the `last_update__gt` filter for incremental syncs.'
        ),
    },
    {
        'name': 'nutritionplan',
        'description': 'Nutrition plans, referencing meals and items by ID.',
    },
    {
        'name': 'nutritionplaninfo',
        'description': (
            'The same plans read-only, with meals, items and their nutritional values '
            'expanded inline. Meant for external tools and integrations that want a whole '
            'plan in one request, with no IDs left to resolve.'
        ),
    },
    {
        'name': 'routine',
        'description': (
            'Workout routines. The nested day, slot and config structure is available in '
            'one request under `/routine/{id}/structure/`.'
        ),
    },
    {
        'name': 'templates',
        'description': (
            'Read-only view of the routines the user marked as a template, plus their '
            "trainer's, if they have one."
        ),
    },
    {
        'name': 'public-templates',
        'description': 'Read-only view of the routine templates published by other users.',
    },
    # The config endpoints all follow the same pattern: a value that takes effect
    # on a given iteration of a routine, per slot entry.
    {
        'name': 'weight-config',
        'description': 'Weight for a set, per iteration.',
    },
    {
        'name': 'max-weight-config',
        'description': 'Upper limit for the weight of a set, per iteration.',
    },
    {
        'name': 'repetitions-config',
        'description': 'Repetitions for a set, per iteration.',
    },
    {
        'name': 'max-repetitions-config',
        'description': 'Upper limit for the repetitions of a set, per iteration.',
    },
    {
        'name': 'sets-config',
        'description': 'Number of sets, per iteration.',
    },
    {
        'name': 'max-sets-config',
        'description': 'Upper limit for the number of sets, per iteration.',
    },
    {
        'name': 'rest-config',
        'description': 'Rest between sets, per iteration.',
    },
    {
        'name': 'max-rest-config',
        'description': 'Upper limit for the rest between sets, per iteration.',
    },
    {
        'name': 'rir-config',
        'description': 'Reps in reserve for a set, per iteration.',
    },
    {
        'name': 'max-rir-config',
        'description': 'Upper limit for the reps in reserve of a set, per iteration.',
    },
]

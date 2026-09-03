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
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language

# Third Party
from drf_spectacular.generators import SchemaGenerator
from rest_framework import serializers

# wger
from wger.utils.cache import CacheKeyMapper
from wger.version import get_version_with_git


class ThumbnailsSerializer(serializers.Serializer):
    """
    Shape of the ``thumbnails`` field, used for schema generation only.

    The aliases are read from settings.THUMBNAIL_ALIASES and are the same for
    every thumbnailed image in the API. Without this, the generated schema falls
    back to a plain string for the dict the method fields return.
    """

    small = serializers.URLField()
    medium = serializers.URLField()


class ThumbnailAliasSerializer(serializers.Serializer):
    """
    One generated thumbnail: where it is and the size it was generated for.
    """

    url = serializers.URLField()
    settings = serializers.DictField()


class ImageThumbnailsSerializer(serializers.Serializer):
    """
    An image's thumbnails, one entry per available size, plus the original.
    """

    small = ThumbnailAliasSerializer()
    medium = ThumbnailAliasSerializer()
    original = serializers.URLField()


def strip_patch_defaults(result, generator, **kwargs):
    """
    Drops ``default`` from the PATCH request bodies.

    An omitted field in a PATCH means "leave this alone", never "set it to
    this". DRF adds the default so the tuple of a UniqueConstraint can be built
    from a payload that omits one of its fields
    (``ModelSerializer.get_uniqueness_extra_kwargs``), which only applies on
    create: on update the validator reads the missing values off the instance.

    It matters because generated clients send a schema default with every
    request. For ``Measurement.source`` that turns an edit to the note of a
    synced entry into a claim that it was hand-entered.
    """
    for name, component in result.get('components', {}).get('schemas', {}).items():
        if not name.startswith('Patched'):
            continue
        for field in component.get('properties', {}).values():
            if isinstance(field, dict):
                field.pop('default', None)

    return result


class CachedSchemaGenerator(SchemaGenerator):
    """
    Serves the generated schema out of the cache.

    Only wired into the view, not into DEFAULT_GENERATOR_CLASS: the spectacular
    management command has to keep generating from the current code.
    """

    def get_schema(self, request=None, public=False):
        language = get_language()

        # An explicit ?version= is passed through unfiltered while
        # ALLOWED_VERSIONS is empty, so its value is caller-controlled and must
        # not reach a cache key.
        if settings.DEBUG or self.api_version or language not in dict(settings.LANGUAGES):
            return super().get_schema(request=request, public=public)

        key = CacheKeyMapper.api_schema_key(get_version_with_git(), language)
        schema = cache.get(key)
        if schema is None:
            schema = super().get_schema(request=request, public=public)
            cache.set(key, schema)

        return schema

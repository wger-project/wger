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

# Third Party
from rest_framework import serializers


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

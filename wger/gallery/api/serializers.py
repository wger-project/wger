# Third Party
from rest_framework import serializers

# wger
from wger.gallery.models import Image


class ImageSerializer(serializers.ModelSerializer):
    """
    Exercise serializer
    """

    class Meta:
        model = Image
        fields = ['id', 'date', 'image', 'description', 'height', 'width']

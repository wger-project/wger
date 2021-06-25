# Django
from django.forms import (
    DateField,
    ModelForm,
    widgets,
)

# wger
from wger.gallery.models import Image
from wger.utils.constants import DATE_FORMATS
from wger.utils.widgets import Html5DateInput


class ImageForm(ModelForm):
    date = DateField(input_formats=DATE_FORMATS, widget=Html5DateInput())

    class Meta:
        model = Image
        exclude = []
        widgets = {
            'user': widgets.HiddenInput(),
        }

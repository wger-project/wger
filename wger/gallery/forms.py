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

# Python Imaging Library to extract data
from PIL import Image as PilImage
from datetime import datetime

class ImageForm(ModelForm):
    date = DateField(input_formats=DATE_FORMATS, widget=Html5DateInput(), required=False)

    class Meta:
        model = Image
        exclude = []
        widgets = {
            'user': widgets.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Tries to extract date from EXIF metadata
        if 'image' in self.changed_data:
            exif_date = self._get_exif_date(self.cleaned_data['image'])
            if exif_date:
                instance.date = exif_date

        if commit:
            instance.save()
        return instance

    def _get_exif_date(self, image_file):
        try:
            img = PilImage.open(image_file)
            exif_data = img._getexif()
            if exif_data:
                # EXIF constant index for date and datetime format
                date_str = exif_data.get(36867)
                if date_str:
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date()
        except Exception as e:
            pass
        return None

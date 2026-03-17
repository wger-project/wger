# Standard Library
from datetime import (
    date,
    datetime,
)

# Django
from django.forms import (
    DateField,
    ModelForm,
    widgets,
)
from django.utils.translation import gettext_lazy

# Third Party
# Python Imaging Library to extract data
from PIL import Image as PilImage

# wger
from wger.gallery.models import Image
from wger.utils.constants import DATE_FORMATS
from wger.utils.widgets import Html5DateInput


class ImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['date'] = None

    date = DateField(
        input_formats=DATE_FORMATS,
        widget=Html5DateInput(),
        required=False,
        help_text=gettext_lazy('If date is left empty, it will be read from the image instead'),
    )

    class Meta:
        model = Image
        exclude = []
        widgets = {
            'user': widgets.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('date'):
            instance.date = self.cleaned_data['date']
        elif 'image' in self.changed_data:
            exif_date = self._get_exif_date(self.cleaned_data['image'])
            instance.date = exif_date if exif_date else date.today()
        else:
            instance.date = date.today()

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

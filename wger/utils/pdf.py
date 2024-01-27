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

# Standard Library
import datetime
from os.path import join as path_join

# Django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation

# Third Party
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import (
    ParagraphStyle,
    StyleSheet1,
)
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
)

# wger
from wger import get_version
from wger.core.models import Language


# ************************
# Language functions
# ************************


def load_language():
    """
    Returns the currently used language, e.g. to load appropriate exercises
    """
    # TODO: perhaps store a language preference in the user's profile?

    # Read the first part of a composite language, e.g. 'de-at'
    used_language = translation.get_language().split('-')[0]

    try:
        language = Language.objects.get(short_name=used_language)

    # No luck, load english as our fall-back language
    except ObjectDoesNotExist:
        language = Language.objects.get(short_name='en')

    return language


def render_footer(url, date=None):
    """
    Renders the footer used in the different PDFs
    :return: a Paragraph object
    """
    if not date:
        date = datetime.date.today().strftime('%d.%m.%Y')

    p = Paragraph(
        f"""<para>
                {date} - <a href="{url}">{url}</a> - wger Workout Manager {get_version()}
            </para>""",
        styleSheet['Normal'],
    )
    return p


def get_logo(width=1.5):
    """
    Returns the wger logo
    """
    image = Image(path_join(settings.SITE_ROOT, 'core/static/images/logos/logo.png'))
    image.drawHeight = width * cm * image.drawHeight / image.drawWidth
    image.drawWidth = width * cm
    return image


# register new truetype fonts for reportlab
pdfmetrics.registerFont(
    TTFont('OpenSans', path_join(settings.SITE_ROOT, 'core/static/fonts/OpenSans-Light.ttf'))
)
pdfmetrics.registerFont(
    TTFont('OpenSans-Bold', path_join(settings.SITE_ROOT, 'core/static/fonts/OpenSans-Bold.ttf'))
)
pdfmetrics.registerFont(
    TTFont(
        'OpenSans-Regular', path_join(settings.SITE_ROOT, 'core/static/fonts/OpenSans-Regular.ttf')
    )
)
pdfmetrics.registerFont(
    TTFont(
        'OpenSans-Italic',
        path_join(settings.SITE_ROOT, 'core/static/fonts/OpenSans-LightItalic.ttf'),
    )
)

styleSheet = StyleSheet1()
styleSheet.add(
    ParagraphStyle(
        name='Normal',
        fontName='OpenSans',
        fontSize=10,
        leading=12,
    )
)
styleSheet.add(
    ParagraphStyle(
        parent=styleSheet['Normal'],
        fontSize=8,
        name='Small',
    )
)
styleSheet.add(
    ParagraphStyle(
        parent=styleSheet['Normal'],
        fontSize=7,
        name='ExerciseComments',
        fontName='OpenSans-Italic',
    )
)
styleSheet.add(
    ParagraphStyle(
        parent=styleSheet['Normal'],
        name='HeaderBold',
        fontSize=16,
        fontName='OpenSans-Bold',
    )
)
styleSheet.add(
    ParagraphStyle(
        parent=styleSheet['Normal'],
        name='SubHeader',
        fontName='OpenSans-Bold',
        textColor=colors.white,
    )
)
styleSheet.add(
    ParagraphStyle(
        parent=styleSheet['Normal'],
        name='SubHeaderBlack',
        fontName='OpenSans-Bold',
        textColor=colors.black,
    )
)

header_colour = HexColor(0x24416B)
row_color = HexColor(0xD1DEF0)

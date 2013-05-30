# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.core import mail

from wger.exercises.models import Language
from wger.utils.constants import EMAIL_FROM


class LanguageConfig(models.Model):
    '''
    Configuration for languages

    Allows to specify what exercises and ingredients are shown for each language
    '''
    SHOW_ITEM_EXERCISES = '1'
    SHOW_ITEM_INGREDIENTS = '2'
    SHOW_ITEM_LIST = (
        (SHOW_ITEM_EXERCISES, _('Exercises')),
        (SHOW_ITEM_INGREDIENTS, _('Ingredients')),
    )

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 related_name='language_source',
                                 editable=False)
    language_target = models.ForeignKey(Language,
                                        verbose_name=_('Language to configure'),
                                        related_name='language_target',
                                        editable=False)
    item = models.CharField(max_length=2,
                            choices=SHOW_ITEM_LIST,
                            editable=False)
    show = models.BooleanField(default=1)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["item", "language_target", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Config for language {0}".format(self.language)


def init_language_config(sender, instance, created, **kwargs):
    '''
    Creates language config entries when new languages are created
    (all combinations of all languages)
    '''
    for language_source in Language.objects.all():
        for language_target in Language.objects.all():
            if not LanguageConfig.objects.filter(language=language_source)\
                                         .filter(language_target=language_target)\
                                         .exists():

                for item in LanguageConfig.SHOW_ITEM_LIST:
                    config = LanguageConfig()
                    config.language = language_source
                    config.language_target = language_target
                    config.item = item[0]
                    if language_source == language_target:
                        config.show = True
                    else:
                        config.show = False
                    config.save()
post_save.connect(init_language_config, sender=Language)

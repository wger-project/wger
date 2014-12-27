# -*- coding: utf-8 -*-

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


from django.db.models.signals import post_save
from django.dispatch import receiver

from wger.config.models import LanguageConfig
from wger.core.models import Language


@receiver(post_save, sender=Language)
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

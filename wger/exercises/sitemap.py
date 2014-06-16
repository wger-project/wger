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

from django.contrib.sitemaps import Sitemap
from wger.exercises.models import Exercise
from wger.utils.language import load_item_languages
from wger.config.models import LanguageConfig


class ExercisesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        language_list = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
        return Exercise.objects.accepted().filter(language__in=language_list)

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

# Django
from django.contrib.sitemaps import Sitemap

# wger
from wger.nutrition.models import Ingredient


class NutritionSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Ingredient.objects.all()

    def lastmod(self, obj):
        return obj.last_update

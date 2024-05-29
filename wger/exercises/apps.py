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
from django.apps import AppConfig


class ExerciseConfig(AppConfig):
    name = 'wger.exercises'
    verbose_name = 'Exercise'

    def ready(self):
        import wger.exercises.signals

        from actstream import registry

        registry.register(self.get_model('Alias'))
        registry.register(self.get_model('Exercise'))
        registry.register(self.get_model('ExerciseBase'))
        registry.register(self.get_model('ExerciseComment'))
        registry.register(self.get_model('ExerciseImage'))
        registry.register(self.get_model('ExerciseVideo'))

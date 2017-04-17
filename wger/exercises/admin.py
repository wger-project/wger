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

from django.contrib import admin
from wger.core.models import Language

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseComment
from wger.exercises.models import ExerciseCategory
from wger.exercises.models import Muscle


class ExerciseCommentInline(admin.TabularInline):  # admin.StackedInline
    model = ExerciseComment
    extra = 1


class ExerciseAdmin(admin.ModelAdmin):

    inlines = [ExerciseCommentInline]


admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(ExerciseCategory)
admin.site.register(Language)
admin.site.register(Muscle)

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

from django import forms

from wger.exercises.models import ExerciseImage, ExerciseComment


class ExerciseImageForm(forms.ModelForm):
    class Meta:
        model = ExerciseImage
        fields = ('image',
                  'is_main',
                  'license',
                  'license_author')


class CommentForm(forms.ModelForm):
    class Meta:
        model = ExerciseComment
        exclude = ('exercise',)

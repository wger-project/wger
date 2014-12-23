# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def insert_mappings(apps, schema_editor):
    '''
    Insert mappings for bench press, squats and deadlifts
    '''

    mapper1 = apps.get_model("exercises", "ExerciseLanguageMapper")()
    mapper1.save()

    mapper2 = apps.get_model("exercises", "ExerciseLanguageMapper")()
    mapper2.save()

    mapper3 = apps.get_model("exercises", "ExerciseLanguageMapper")()
    mapper3.save()

    for exercise in apps.get_model("exercises", "Exercise").objects.filter(id__in=(192, 15, 111, 7, 105, 9)):

        # Bench
        if exercise.pk in (192, 15):
            exercise.language_mapper = mapper1
            exercise.save()

        # Squats
        if exercise.pk in (111, 7):
            exercise.language_mapper = mapper2
            exercise.save()

        # Deadlifts
        if exercise.pk in (105, 9):
            exercise.language_mapper = mapper3
            exercise.save()

def delete_mappings(apps, schema_editor):
    '''
    Delete all mappings
    '''
    apps.get_model("exercises", "ExerciseLanguageMapper").objects.all().delete()
    apps.get_model("exercises", "Exercise").objects.all().update(language_mapper=None)


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0002_auto_20141223_1414'),
    ]

    operations = [
        migrations.RunPython(insert_mappings, delete_mappings),
    ]

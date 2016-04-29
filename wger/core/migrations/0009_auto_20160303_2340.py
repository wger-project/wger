# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def insert_data(apps, schema_editor):
    '''
    Inserts initial data for repetition and weight units

    Needed so that the migrations can go through without having to load any
    fixtures or perform any intermediate steps.
    '''
    WeightUnit = apps.get_model('core', 'WeightUnit')
    WeightUnit(name='kg', pk=1).save()
    WeightUnit(name='lb', pk=2).save()
    WeightUnit(name='Body Weight', pk=3).save()
    WeightUnit(name='Plates', pk=4).save()
    WeightUnit(name='Kilometers Per Hour', pk=5).save()
    WeightUnit(name='Miles Per Hour', pk=6).save()

    RepetitionUnit = apps.get_model('core', 'RepetitionUnit')
    RepetitionUnit(name='Repetitions', pk=1).save()
    RepetitionUnit(name='Until Failure', pk=2).save()
    RepetitionUnit(name='Seconds', pk=3).save()
    RepetitionUnit(name='Minutes', pk=4).save()
    RepetitionUnit(name='Miles', pk=5).save()
    RepetitionUnit(name='Kilometers', pk=6).save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_weightunit'),
    ]

    operations = [
        migrations.RunPython(insert_data, reverse_code=migrations.RunPython.noop),
    ]

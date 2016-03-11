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
    WeightUnit(name='kg').save()
    WeightUnit(name='lb').save()
    WeightUnit(name='Body Weight').save()
    WeightUnit(name='Plates').save()
    WeightUnit(name='Kilometers Per Hour').save()
    WeightUnit(name='Miles Per Hour').save()

    RepetitionUnit = apps.get_model('core', 'RepetitionUnit')
    RepetitionUnit(name='Repetitions').save()
    RepetitionUnit(name='Until Failure').save()
    RepetitionUnit(name='Seconds').save()
    RepetitionUnit(name='Minutes').save()
    RepetitionUnit(name='Miles').save()
    RepetitionUnit(name='Kilometers').save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_weightunit'),
    ]

    operations = [
        migrations.RunPython(insert_data, reverse_code=migrations.RunPython.noop),
    ]

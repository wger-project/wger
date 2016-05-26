# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def convert_logs(apps, schema_editor):
    '''
    Adds a unit to users who have imperial units in the profile
    '''

    WorkoutLog = apps.get_model('manager', 'WorkoutLog')
    UserProfile = apps.get_model('core', 'UserProfile')

    for profile in UserProfile.objects.filter(weight_unit='lb'):
        WorkoutLog.objects.filter(user=profile.user).update(weight_unit=2)


def convert_settings(apps, schema_editor):
    '''
    Adds a unit to workout settings that have 99 for 'until failure'
    '''

    Setting = apps.get_model('manager', 'Setting')
    Setting.objects.filter(reps=99).update(reps=1, repetition_unit=2)


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_auto_20160303_2138'),
    ]

    operations = [
        migrations.RunPython(convert_logs, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(convert_settings, reverse_code=migrations.RunPython.noop),
    ]

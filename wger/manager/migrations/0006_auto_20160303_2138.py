# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160303_2340'),
        ('manager', '0005_auto_20160303_2008'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='unit',
            new_name='repetition_unit',
        ),
        migrations.RenameField(
            model_name='workoutlog',
            old_name='unit',
            new_name='repetition_unit',
        ),
        migrations.AddField(
            model_name='setting',
            name='weight_unit',
            field=models.ForeignKey(verbose_name='Unit', to='core.WeightUnit', default=1),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='weight_unit',
            field=models.ForeignKey(verbose_name='Unit', to='core.WeightUnit', default=1),
        ),
    ]

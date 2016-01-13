# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160113_1018'),
        ('manager', '0005_auto_20160107_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='workoutlog',
            name='unit',
            field=models.ForeignKey(verbose_name='Unit', to='core.SettingUnit', default=1),
        ),
        migrations.AlterField(
            model_name='setting',
            name='reps',
            field=models.IntegerField(verbose_name='Amount', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='setting',
            name='unit',
            field=models.ForeignKey(verbose_name='Unit', to='core.SettingUnit', default=1),
        ),
    ]

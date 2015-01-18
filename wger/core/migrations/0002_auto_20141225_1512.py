# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ro_access',
            field=models.BooleanField(help_text='Allow anonymous users to access your workouts and logs in a read-only mode. You can  then share the links to social media.', verbose_name='Allow read-only access', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='freetime_intensity',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], null=True, max_length=1, help_text='Approximately', default='1', verbose_name='Physical intensity'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('1', 'Male'), ('2', 'Female')], null=True, default='1', max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sport_intensity',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], null=True, max_length=1, help_text='Approximately', default='2', verbose_name='Physical intensity'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='weight_unit',
            field=models.CharField(choices=[('kg', 'Metric (kilogram)'), ('lb', 'Imperial (pound)')], verbose_name='Weight unit', max_length=2, default='kg'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='work_intensity',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], null=True, max_length=1, help_text='Approximately', default='1', verbose_name='Physical intensity'),
            preserve_default=True,
        ),
    ]

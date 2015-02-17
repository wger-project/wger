# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20141225_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='num_days_weight_reminder',
            field=models.IntegerField(verbose_name='Automatic reminders for weight entries', max_length=30, null=True, help_text='Number of days after the last weight entry (enter 0 to deactivate)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='age',
            field=models.IntegerField(verbose_name='Age', null=True, validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(100)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='height',
            field=models.IntegerField(verbose_name='Height (cm)', null=True, validators=[django.core.validators.MinValueValidator(140), django.core.validators.MaxValueValidator(230)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='ro_access',
            field=models.BooleanField(verbose_name='Allow external access', default=False, help_text='Allow external users to access your workouts and logs in a read-only mode. You need to set this before you can share links e.g. to social media.'),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gym', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gym',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gym',
            name='zip_code',
            field=models.CharField(max_length=10, verbose_name='ZIP code', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gymconfig',
            name='weeks_inactive',
            field=models.PositiveIntegerField(help_text='Number of weeks since the last time a user logged his presence to be considered inactive', default=4, verbose_name='Reminder inactive members'),
        ),
    ]
